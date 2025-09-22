"""
Advanced AST parsing utilities for documentation tooling.

Shared AST parsing functionality developed during endpoint and model validation work.
Handles complex type annotations, generic types, and Python implementation analysis.
"""

import ast
from pathlib import Path
from typing import Any


class ASTTypeParser:
    """Enhanced AST type annotation parser with full generic support."""

    @staticmethod
    def get_type_string(node: ast.AST) -> str:
        """
        Convert AST type annotation to string.

        Enhanced to handle complex generic types like dict[str, Any], list[TradeID],
        union types, and tuple slices for multiple generic parameters.
        """
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Attribute):
            value = ASTTypeParser.get_type_string(node.value)
            return f"{value}.{node.attr}"
        if isinstance(node, ast.Subscript):
            value = ASTTypeParser.get_type_string(node.value)
            if isinstance(node.slice, ast.Tuple):
                # Handle multiple generic parameters like dict[str, Any]
                slice_parts = [ASTTypeParser.get_type_string(elt) for elt in node.slice.elts]
                slice_val = ", ".join(slice_parts)
            else:
                slice_val = ASTTypeParser.get_type_string(node.slice)
            return f"{value}[{slice_val}]"
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            left = ASTTypeParser.get_type_string(node.left)
            right = ASTTypeParser.get_type_string(node.right)
            return f"{left} | {right}"
        return str(node)

    @staticmethod
    def get_value_string(value: ast.AST) -> str:
        """Convert AST value to string representation."""
        if isinstance(value, ast.Constant):
            return repr(value.value)
        if isinstance(value, ast.Name):
            return value.id
        if isinstance(value, ast.Attribute):
            return f"{value.value.id}.{value.attr}" if hasattr(value.value, "id") else str(value.attr)
        return str(value)


class MethodExtractor:
    """Extracts method information from Python AST."""

    def __init__(self) -> None:
        self.type_parser = ASTTypeParser()

    def extract_method_info(self, method_node: ast.FunctionDef, content: str, file_path: str) -> dict[str, Any]:
        """Extract comprehensive method information from AST node."""
        method_name = method_node.name
        docstring = ast.get_docstring(method_node) or ""

        # Extract parameters
        parameters = {}
        for arg in method_node.args.args:
            if arg.arg != "self":  # Skip self parameter
                param_info = self._extract_parameter_info(arg, method_node)
                if param_info:
                    parameters[param_info["name"]] = param_info

        # **kwargs parameter detection
        has_kwargs = method_node.args.kwarg is not None

        # Extract return type
        return_type = "Any"
        if method_node.returns:
            return_type = self.type_parser.get_type_string(method_node.returns)

        return {"name": method_name, "parameters": parameters, "return_type": return_type, "docstring": docstring, "file_path": file_path, "has_kwargs": has_kwargs}

    def _extract_parameter_info(self, arg: ast.arg, method_node: ast.FunctionDef) -> dict[str, Any] | None:
        """Extract parameter information including type, default, and required status."""
        param_name = arg.arg
        type_annotation = "Any"

        if arg.annotation:
            type_annotation = self.type_parser.get_type_string(arg.annotation)

        # Check for default values
        default = None
        required = True

        # Get defaults from method signature
        defaults = method_node.args.defaults
        args = method_node.args.args

        # Calculate if this parameter has a default
        if len(defaults) > 0:
            # defaults are aligned with the last N parameters
            defaults_start_index = len(args) - len(defaults)
            param_index = next((i for i, a in enumerate(args) if a.arg == param_name), -1)

            if param_index >= defaults_start_index:
                default_index = param_index - defaults_start_index
                if default_index < len(defaults):
                    default = self.type_parser.get_value_string(defaults[default_index])
                    required = False

        # Handle optional types
        if " | None" in type_annotation or "Optional[" in type_annotation:
            required = False

        return {"name": param_name, "type_annotation": type_annotation, "default": default, "required": required}


class ModelExtractor:
    """Extracts model information from Python AST."""

    def __init__(self) -> None:
        self.type_parser = ASTTypeParser()

    def extract_model_info(self, class_node: ast.ClassDef, content: str, file_path: str) -> dict[str, Any]:
        """Extract comprehensive model information from AST node."""
        model_name = class_node.name
        docstring = ast.get_docstring(class_node) or ""

        # Extract base classes
        base_classes = []
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                if hasattr(base.value, 'id'):
                    base_classes.append(f"{base.value.id}.{base.attr}")
                else:
                    base_classes.append(f"{base.attr}")

        # Extract fields
        fields = {}
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                field_name = node.target.id
                field_info = self._extract_field_info(node, content)
                fields[field_name] = field_info

        return {"name": model_name, "file_path": file_path, "docstring": docstring, "fields": fields, "base_classes": base_classes}

    def _extract_field_info(self, ann_assign: ast.AnnAssign, content: str) -> dict[str, Any]:
        """Extract field information including type, alias, default."""
        if not isinstance(ann_assign.target, ast.Name):
            return {"name": "", "type_annotation": "Any", "alias": None, "default": None, "required": True, "description": None}
        field_name = ann_assign.target.id
        type_annotation = self.type_parser.get_type_string(ann_assign.annotation)

        alias = None
        default = None
        required = True
        description = None

        # Extract Field() information if present
        if ann_assign.value:
            if isinstance(ann_assign.value, ast.Call) and isinstance(ann_assign.value.func, ast.Name):
                if ann_assign.value.func.id == "Field":
                    # Parse Field arguments
                    if ann_assign.value.args:
                        # First positional argument is often default value
                        default = self.type_parser.get_value_string(ann_assign.value.args[0])
                        if default in ["None", "...", "Ellipsis"]:
                            required = False

                    # Parse keyword arguments
                    for keyword in ann_assign.value.keywords:
                        if keyword.arg == "alias":
                            alias = self.type_parser.get_value_string(keyword.value)
                        elif keyword.arg == "default":
                            default = self.type_parser.get_value_string(keyword.value)
                            required = False
                        elif keyword.arg == "description":
                            description = self.type_parser.get_value_string(keyword.value)
            else:
                # Direct default value assignment
                default = self.type_parser.get_value_string(ann_assign.value)
                required = False

        # Handle optional types
        if " | None" in type_annotation or "Optional[" in type_annotation:
            required = False

        return {"name": field_name, "type_annotation": type_annotation, "alias": alias, "default": default, "required": required, "description": description}

    def is_model_class(self, class_node: ast.ClassDef) -> bool:
        """Check if this is a model class (inherits from BaseModel, ApiModel, etc.)"""
        return any((isinstance(base, ast.Name) and "Model" in base.id) or (isinstance(base, ast.Attribute) and "Model" in base.attr) for base in class_node.bases)


class PythonCodeAnalyzer:
    """High-level analyzer for Python code using AST."""

    def __init__(self) -> None:
        self.method_extractor = MethodExtractor()
        self.model_extractor = ModelExtractor()

    def extract_methods_from_file(self, file_path: str) -> list[dict[str, Any]]:
        """Extract all methods from a Python file."""
        methods = []

        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    method_info = self.method_extractor.extract_method_info(node, content, file_path)
                    methods.append(method_info)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return methods

    def extract_models_from_file(self, file_path: str) -> list[dict[str, Any]]:
        """Extract all model classes from a Python file."""
        models = []

        try:
            with Path(file_path).open(encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self.model_extractor.is_model_class(node):
                        model_info = self.model_extractor.extract_model_info(node, content, file_path)
                        models.append(model_info)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return models
