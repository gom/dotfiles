class Toml:
    @staticmethod
    def dict_to_toml(data):
        """
        Lightweight standard-library TOML serializer supporting nested tables
        and arrays of tables (fix #4: lists of dicts now render as [[section]]).
        """
        output = []

        def serialize(d, prefix=""):
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
    def _toml_value(v):
        """Serialize a scalar Python value to a TOML value string."""
        if isinstance(v, str):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(v, bool):
            return str(v).lower()
        if isinstance(v, list):
            items = []
            for x in v:
                if isinstance(x, str):
                    esc = x.replace("\\", "\\\\").replace('"', '\\"')
                    items.append(f'"{esc}"')
                elif isinstance(x, bool):
                    items.append(str(x).lower())
                else:
                    items.append(str(x))
            return f"[{', '.join(items)}]"
        if v is None:
            return '""'
        return str(v)

    @staticmethod
    def parse_toml(content):
        """
        Lightweight line-by-line TOML parser for basic flat/nested configs.
        Replaced with native tomllib for Python 3.11+ support.
        """
        import tomllib
        return tomllib.loads(content)
