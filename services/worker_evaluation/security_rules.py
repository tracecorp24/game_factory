"""
Workflow Security Rules, AST Allowlist/Blocklist, and SSRF/Path-Traversal Validators.
CreativeForge Intelligence Studio v3.0 - ComfyUI Hybrid Integration (Agent H-4).
"""

from __future__ import annotations

import ipaddress
import os
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse
from pydantic import BaseModel, Field

from services.worker_evaluation.gates.base import GateSeverity


class SecurityViolationType(str, Enum):
    """Specific category of security violation detected in a workflow."""
    UNAUTHORIZED_NODE_CLASS = "UNAUTHORIZED_NODE_CLASS"
    DANGEROUS_NODE_EXECUTION = "DANGEROUS_NODE_EXECUTION"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    SSRF_ATTEMPT = "SSRF_ATTEMPT"
    UNSAFE_SCRIPT = "UNSAFE_SCRIPT"
    MALFORMED_GRAPH = "MALFORMED_GRAPH"


# Standard, vetted, and approved ComfyUI node classes
APPROVED_COMFY_NODE_ALLOWLIST: Set[str] = {
    # Checkpoint & Model Loaders
    "CheckpointLoaderSimple",
    "CheckpointLoader",
    "unCLIPCheckpointLoader",
    "VAELoader",
    "CLIPLoader",
    "DualCLIPLoader",
    "LoraLoader",
    "LoraLoaderModelOnly",
    "DiffusersLoader",
    "UNETLoader",
    "CLIPVisionLoader",

    # Conditioning & Text Encoding
    "CLIPTextEncode",
    "CLIPTextEncodeSDXL",
    "CLIPTextEncodeFlux",
    "CLIPSetLastLayer",
    "ConditioningCombine",
    "ConditioningAverage",
    "ConditioningConcat",
    "ConditioningSetArea",
    "ConditioningSetMask",
    "ConditioningZeroOut",

    # Sampling & Latents
    "KSampler",
    "KSamplerAdvanced",
    "KSamplerSelect",
    "SamplerCustom",
    "SamplerCustomAdvanced",
    "BasicScheduler",
    "SDTurboScheduler",
    "BetaScheduler",
    "EmptyLatentImage",
    "EmptyLatentImageSDXL",
    "LatentUpscale",
    "LatentUpscaleBy",
    "LatentComposite",
    "LatentCrop",
    "LatentBlend",
    "VAEDecode",
    "VAEEncode",
    "VAEDecodeTiled",
    "VAEEncodeTiled",
    "VAEDecodeAudio",
    "VAEEncodeAudio",

    # Safe Image & Mask Handling
    "LoadImage",
    "SaveImage",
    "PreviewImage",
    "ImageScale",
    "ImageScaleBy",
    "ImageInvert",
    "ImageBatch",
    "ImagePadForOutpaint",
    "ImageCompositeMasked",
    "CropImage",
    "ImageColorToMask",
    "ImageToMask",
    "MaskToImage",
    "ImageBlend",
    "ImageBlur",
    "LoadImageMask",
    "SolidMask",
    "InvertMask",
    "CropMask",
    "FeatherMask",
    "MaskComposite",

    # ControlNet & Adapters
    "ControlNetLoader",
    "ControlNetApply",
    "ControlNetApplyAdvanced",
    "DiffControlNetLoader",
    "IPAdapter",
    "IPAdapterModelLoader",
    "IPAdapterApply",
    "IPAdapterApplyFaceID",
    "IPAdapterUnifiedLoader",
    "IPAdapterFaceID",

    # UI, Routing & Utilities
    "PrimitiveNode",
    "Reroute",
    "Note",
    "Cast",
    "DisplayAny",
}

# Explicit blocklist of dangerous node classes (arbitrary code, shell, or raw filesystem access)
DANGEROUS_NODE_CLASSES: Set[str] = {
    "PythonExec",
    "RunCommand",
    "CustomScript",
    "SaveImageToSystemPath",
    "LoadExternalFile",
    "ExecuteCode",
    "ShellExecute",
    "BashCommand",
    "SystemCommand",
    "EvalPython",
    "UnsafePython",
    "FileWriteNode",
    "RawPythonCode",
    "CustomPythonScript",
    "ExternalCommandNode",
    "OSExecNode",
    "SubprocessNode",
    "TerminalNode",
    "ArbitraryCodeNode",
}

# Allowed remote model / asset download domains for SSRF defense
ALLOWED_EXTERNAL_DOMAINS: Set[str] = {
    "huggingface.co",
    "civitai.com",
    "models.creativeforge.ai",
    "cdn.creativeforge.ai",
    "storage.creativeforge.ai",
    "github.com",
    "raw.githubusercontent.com",
}


def get_effective_allowed_domains(additional_domains: Optional[Union[Set[str], List[str]]] = None) -> Set[str]:
    """
    Returns unified set of approved asset download domains combining:
    1. Built-in trusted defaults (HuggingFace, Civitai, CreativeForge CDN, GitHub)
    2. Environment variable COMFY_ALLOWED_DOMAINS (comma-separated, e.g. AWS S3, GCS, Azure, enterprise MinIO)
    3. Runtime or Game DNA overrides passed in parameters
    """
    domains = set(ALLOWED_EXTERNAL_DOMAINS)

    # 1. Environment variable overrides (e.g. "s3.amazonaws.com,storage.googleapis.com,minio.corp.internal")
    env_domains = os.getenv("COMFY_ALLOWED_DOMAINS", "").strip()
    if env_domains:
        for d in env_domains.split(","):
            d_clean = d.strip().lower()
            if d_clean:
                domains.add(d_clean)

    # 2. Contextual / runtime additional domains
    if additional_domains:
        for d in additional_domains:
            d_clean = str(d).strip().lower()
            if d_clean:
                domains.add(d_clean)

    return domains

# Path traversal detection regexes and indicators
PATH_TRAVERSAL_PATTERNS = [
    re.compile(r"\.\.[/\\]"),                     # ../ or ..\
    re.compile(r"^[A-Za-z]:[/\\]"),                # Windows drive letter C:\ or C:/
    re.compile(r"^/[a-zA-Z0-9_-]+"),               # Unix root paths e.g. /etc, /var, /root
    re.compile(r"^\\\\"),                          # Windows UNC share \\server\share
    re.compile(r"(?:/etc/|/var/|/root/|/proc/|/tmp/|/bin/|/usr/|/windows/|/system32/)", re.IGNORECASE),
    re.compile(r"(?:windows[/\\]system32)", re.IGNORECASE),
]

# Sensitive system files that must never be targeted
FORBIDDEN_FILE_TARGETS = {
    "passwd",
    "shadow",
    "hosts",
    "sam",
    "system",
    "win.ini",
    "boot.ini",
    ".env",
    "id_rsa",
    "id_ed25519",
}

# Dangerous Python code patterns inside string parameters
SUSPICIOUS_SCRIPT_SNIPPETS = [
    re.compile(r"\b__import__\s*\(", re.IGNORECASE),
    re.compile(r"\bimportlib\b", re.IGNORECASE),
    re.compile(r"\beval\s*\(", re.IGNORECASE),
    re.compile(r"\bexec\s*\(", re.IGNORECASE),
    re.compile(r"\bos\.(?:system|popen|spawn|exec|remove|unlink|rmdir)\s*\(", re.IGNORECASE),
    re.compile(r"\bsubprocess\.(?:Popen|run|call|check_output)\s*\(", re.IGNORECASE),
    re.compile(r"\bshutil\.(?:rmtree|copyfile|copy|move)\s*\(", re.IGNORECASE),
    re.compile(r"\bopen\s*\(", re.IGNORECASE),
]


class SecurityIssue(BaseModel):
    """Details of a single security issue identified during AST inspection."""
    severity: GateSeverity = GateSeverity.FATAL
    issue_type: SecurityViolationType
    node_id: Optional[str] = None
    node_class: Optional[str] = None
    field_name: Optional[str] = None
    offending_value: Optional[str] = None
    message: str


class SecurityScanReport(BaseModel):
    """Aggregate report produced by the Workflow Security Linter."""
    is_safe: bool = True
    scanned_nodes_count: int = 0
    issues: List[SecurityIssue] = Field(default_factory=list)
    failure_code: Optional[str] = None
    summary: str = "Workflow AST verified secure."

    def add_issue(self, issue: SecurityIssue) -> None:
        self.issues.append(issue)
        if issue.severity in (GateSeverity.FATAL, GateSeverity.ERROR):
            self.is_safe = False
            self.failure_code = "WORKFLOW_SECURITY_VIOLATION"


def is_ip_private_or_loopback(host: str) -> bool:
    """Check if a host is localhost, private IP range, link-local or loopback."""
    host_clean = host.strip("[]").lower()
    if host_clean in ("localhost", "0.0.0.0", "127.0.0.1", "::1", "metadata.google.internal"):
        return True
    try:
        ip = ipaddress.ip_address(host_clean)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
        )
    except ValueError:
        return False


def validate_url_security(
    url_str: str,
    allowed_domains: Optional[Set[str]] = None,
) -> Tuple[bool, Optional[str]]:
    """Validate external URLs against SSRF, dangerous schemes, and host allowlist."""
    try:
        parsed = urlparse(url_str)
    except Exception as e:
        return False, f"Malformed URL '{url_str}': {str(e)}"

    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Forbidden URL scheme '{parsed.scheme}'; only HTTP/HTTPS are allowed."

    host = parsed.hostname
    if not host:
        return False, f"URL has no valid hostname: '{url_str}'"

    # Check for private or loopback IP addresses (SSRF)
    if is_ip_private_or_loopback(host):
        return False, f"SSRF blocked: Host '{host}' resolves to private/loopback/metadata address."

    # Verify domain allowlist
    target_allowlist = allowed_domains if allowed_domains is not None else get_effective_allowed_domains()
    host_lower = host.lower()
    is_allowed = any(
        host_lower == allowed or host_lower.endswith(f".{allowed}")
        for allowed in target_allowlist
    )
    if not is_allowed:
        return False, f"Domain '{host}' is not in approved external asset domain allowlist."

    return True, None


def check_path_traversal(val_str: str) -> Optional[str]:
    """Scan a string value for directory traversal or sensitive file references."""
    val_norm = val_str.replace("\\", "/")

    # Check forbidden specific sensitive targets
    base_name = os.path.basename(val_norm).lower()
    if base_name in FORBIDDEN_FILE_TARGETS:
        return f"Forbidden sensitive system file access attempt: '{base_name}'"

    # Check path traversal patterns
    for pat in PATH_TRAVERSAL_PATTERNS:
        if pat.search(val_str) or pat.search(val_norm):
            return f"Path traversal pattern detected in file reference: '{val_str}'"

    return None


def check_unsafe_code(val_str: str) -> Optional[str]:
    """Check if a string contains executable Python code or OS calls."""
    for pat in SUSPICIOUS_SCRIPT_SNIPPETS:
        match = pat.search(val_str)
        if match:
            return f"Unsafe script pattern '{match.group(0)}' detected in input."
    return None


class WorkflowSecurityLinter:
    """
    Statical AST Linter and Security Analyzer for ComfyUI workflows.
    Supports both ComfyUI API Prompt format and ComfyUI UI format.
    """

    def __init__(
        self,
        node_allowlist: Optional[Set[str]] = None,
        node_blocklist: Optional[Set[str]] = None,
        allowed_domains: Optional[Union[Set[str], List[str]]] = None,
        enforce_allowlist: bool = True,
    ):
        self.node_allowlist = set(node_allowlist) if node_allowlist is not None else APPROVED_COMFY_NODE_ALLOWLIST
        self.node_blocklist = set(node_blocklist) if node_blocklist is not None else DANGEROUS_NODE_CLASSES
        self.allowed_domains = get_effective_allowed_domains(allowed_domains)
        self.enforce_allowlist = enforce_allowlist

    def lint(self, workflow_data: Union[Dict[str, Any], List[Any]]) -> SecurityScanReport:
        """Execute full security inspection over workflow graph data."""
        report = SecurityScanReport()

        if not isinstance(workflow_data, (dict, list)):
            report.add_issue(
                SecurityIssue(
                    severity=GateSeverity.FATAL,
                    issue_type=SecurityViolationType.MALFORMED_GRAPH,
                    message="Workflow payload must be a JSON dictionary or array.",
                )
            )
            report.summary = "Malformed workflow: Root object must be a dictionary or list."
            return report

        # Detect format: ComfyUI UI format has "nodes" array; ComfyUI API format maps node_id -> dict
        nodes_dict: Dict[str, Dict[str, Any]] = {}

        if isinstance(workflow_data, dict) and "nodes" in workflow_data and isinstance(workflow_data["nodes"], list):
            # ComfyUI UI format
            for node_item in workflow_data["nodes"]:
                if isinstance(node_item, dict):
                    node_id = str(node_item.get("id", len(nodes_dict)))
                    node_type = str(node_item.get("type", ""))
                    inputs = {}
                    # Extract widgets_values or properties
                    if "widgets_values" in node_item and isinstance(node_item["widgets_values"], list):
                        inputs["widgets_values"] = node_item["widgets_values"]
                    if "properties" in node_item and isinstance(node_item["properties"], dict):
                        inputs.update(node_item["properties"])
                    nodes_dict[node_id] = {
                        "class_type": node_type,
                        "inputs": inputs,
                    }
        elif isinstance(workflow_data, dict):
            # ComfyUI API Prompt format: { "node_id": { "class_type": "...", "inputs": { ... } } }
            for k, v in workflow_data.items():
                if isinstance(v, dict) and "class_type" in v:
                    nodes_dict[str(k)] = v
                elif isinstance(v, dict) and "inputs" in v:
                    # In some variations, class_type might be named type
                    v_class = v.get("class_type") or v.get("type", "Unknown")
                    nodes_dict[str(k)] = {"class_type": str(v_class), "inputs": v.get("inputs", {})}

        report.scanned_nodes_count = len(nodes_dict)

        if not nodes_dict:
            # If payload was empty or non-empty dict without recognized nodes
            if isinstance(workflow_data, dict) and len(workflow_data) > 0 and "nodes" not in workflow_data:
                # Could be raw empty graph or invalid structure
                report.add_issue(
                    SecurityIssue(
                        severity=GateSeverity.ERROR,
                        issue_type=SecurityViolationType.MALFORMED_GRAPH,
                        message="Workflow dictionary does not contain valid ComfyUI node definitions.",
                    )
                )
                report.summary = "Workflow contains no recognizable ComfyUI nodes."
                return report

        # Inspect each node
        for node_id, node_spec in nodes_dict.items():
            class_type = str(node_spec.get("class_type", "")).strip()

            # 1. Check Explicit Dangerous Blocklist
            if class_type in self.node_blocklist:
                report.add_issue(
                    SecurityIssue(
                        severity=GateSeverity.FATAL,
                        issue_type=SecurityViolationType.DANGEROUS_NODE_EXECUTION,
                        node_id=node_id,
                        node_class=class_type,
                        message=f"Dangerous uncontained execution node class '{class_type}' detected in node {node_id}.",
                    )
                )

            # 2. Check Approved Allowlist
            elif self.enforce_allowlist and class_type not in self.node_allowlist:
                report.add_issue(
                    SecurityIssue(
                        severity=GateSeverity.FATAL,
                        issue_type=SecurityViolationType.UNAUTHORIZED_NODE_CLASS,
                        node_id=node_id,
                        node_class=class_type,
                        message=f"Unauthorized custom node class '{class_type}' in node {node_id}. Node is not in APPROVED_COMFY_NODE_ALLOWLIST.",
                    )
                )

            # 3. Check Inputs for Path Traversal, SSRF, and Unsafe Code
            inputs = node_spec.get("inputs", {})
            self._scan_inputs(node_id, class_type, inputs, report)

        if not report.is_safe:
            violation_types = {issue.issue_type.value for issue in report.issues}
            report.summary = (
                f"Security scan FAILED with {len(report.issues)} issue(s): {', '.join(sorted(violation_types))}."
            )
        else:
            report.summary = f"Security scan PASSED. All {report.scanned_nodes_count} nodes verified against AST allowlist."

        return report

    def _scan_inputs(
        self,
        node_id: str,
        class_type: str,
        data: Any,
        report: SecurityScanReport,
        current_field: str = "",
    ) -> None:
        """Recursively scan node inputs, widgets, and attributes for security violations."""
        if isinstance(data, dict):
            for k, v in data.items():
                field_name = f"{current_field}.{k}" if current_field else str(k)
                self._scan_inputs(node_id, class_type, v, report, field_name)

        elif isinstance(data, list):
            for idx, item in enumerate(data):
                field_name = f"{current_field}[{idx}]"
                self._scan_inputs(node_id, class_type, item, report, field_name)

        elif isinstance(data, str):
            val_str = data.strip()

            # A. Check URL / SSRF
            if val_str.startswith("http://") or val_str.startswith("https://") or "://" in val_str:
                is_safe_url, url_err = validate_url_security(val_str, self.allowed_domains)
                if not is_safe_url:
                    report.add_issue(
                        SecurityIssue(
                            severity=GateSeverity.FATAL,
                            issue_type=SecurityViolationType.SSRF_ATTEMPT,
                            node_id=node_id,
                            node_class=class_type,
                            field_name=current_field,
                            offending_value=val_str,
                            message=url_err or "Insecure or prohibited URL detected.",
                        )
                    )

            # B. Check Path Traversal (especially on file/ckpt/model/dir fields)
            is_file_field = any(
                tag in current_field.lower()
                for tag in ("ckpt", "model", "path", "file", "lora", "vae", "control_net", "name", "dir")
            )
            # Check traversal patterns for file fields or anything with slashes/colons
            if is_file_field or "/" in val_str or "\\" in val_str or ":" in val_str or val_str.startswith("."):
                traversal_err = check_path_traversal(val_str)
                if traversal_err:
                    report.add_issue(
                        SecurityIssue(
                            severity=GateSeverity.FATAL,
                            issue_type=SecurityViolationType.PATH_TRAVERSAL,
                            node_id=node_id,
                            node_class=class_type,
                            field_name=current_field,
                            offending_value=val_str,
                            message=traversal_err,
                        )
                    )

            # C. Check Embedded Unsafe Code
            code_err = check_unsafe_code(val_str)
            if code_err:
                report.add_issue(
                    SecurityIssue(
                        severity=GateSeverity.FATAL,
                        issue_type=SecurityViolationType.UNSAFE_SCRIPT,
                        node_id=node_id,
                        node_class=class_type,
                        field_name=current_field,
                        offending_value=val_str[:60] + "..." if len(val_str) > 60 else val_str,
                        message=code_err,
                    )
                )
