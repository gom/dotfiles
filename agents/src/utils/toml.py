import tomllib


class Toml:
    @staticmethod
    def parse_toml(content: str) -> dict:
        """Parse TOML content using the stdlib tomllib (Python 3.11+)."""
        return tomllib.loads(content)

    @staticmethod
    def dict_to_toml(data: dict) -> str:
        """
        Serialize a Python dict to a TOML string.
        Supports nested tables ([section]) and arrays of tables ([[section]]).
        """
        output = []

        def serialize(d: dict, prefix: str = ""):
            # First pass: scalar key-value pairs
            for k, v in sorted(d.items()):
                if isinstance(v, dict):
                    continue
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    continue  # handled below as [[array-of-tables]]
                output.append(f"{k} = {Toml._toml_value(v)}")

            # Second pass: nested dicts as [table], lists-of-dicts as [[table]]
            for k, v in sorted(d.items()):
                table_header = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    output.append(f"\n[{table_header}]")
                    serialize(v, table_header)
                elif isinstance(v, list) and v and isinstance(v[0], dict):
                    for item in v:
                        output.append(f"\n[[{table_header}]]")
                        for ik, iv in sorted(item.items()):
                            output.append(f"{ik} = {Toml._toml_value(iv)}")

        serialize(data)
        return "\n".join(output)

    @staticmethod
    def _toml_value(v) -> str:
        """Serialize a scalar Python value to a TOML value string."""
        if isinstance(v, bool):
            return str(v).lower()
        if isinstance(v, str):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(v, list):
            items = []
            for x in v:
                if isinstance(x, bool):
                    items.append(str(x).lower())
                elif isinstance(x, str):
                    esc = x.replace("\\", "\\\\").replace('"', '\\"')
                    items.append(f'"{esc}"')
                else:
                    items.append(str(x))
            return f"[{', '.join(items)}]"
        if v is None:
            return '""'
        return str(v)
