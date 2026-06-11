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
        Limitations (fix #5 documented): no inline tables, no multi-line strings,
        no array-of-tables (lines starting with [[) — sufficient for Codex
        config.toml round-trips on keys produced by dict_to_toml.
        """
        data = {}
        current_table = data

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Standard table header (skip [[...]] array-of-tables lines)
            if line.startswith("[") and line.endswith("]") and not line.startswith("[["):
                table_name = line[1:-1].strip()
                current_table = data
                for part in table_name.split("."):
                    part = part.strip()
                    if part not in current_table or not isinstance(current_table[part], dict):
                        current_table[part] = {}
                    current_table = current_table[part]
            elif "=" in line:
                key, val_str = line.split("=", 1)
                key = key.strip()
                val_str = val_str.strip()

                if val_str.startswith("[") and val_str.endswith("]"):
                    items = []
                    inner = val_str[1:-1].strip()
                    if inner:
                        for x in inner.split(","):
                            x = x.strip()
                            if x.startswith('"') and x.endswith('"'):
                                items.append(x[1:-1].replace('\\"', '"'))
                            elif x == "true":
                                items.append(True)
                            elif x == "false":
                                items.append(False)
                            else:
                                try:
                                    items.append(int(x))
                                except ValueError:
                                    items.append(x)
                    current_table[key] = items
                elif val_str.startswith('"') and val_str.endswith('"'):
                    current_table[key] = val_str[1:-1].replace('\\"', '"')
                elif val_str == "true":
                    current_table[key] = True
                elif val_str == "false":
                    current_table[key] = False
                else:
                    try:
                        current_table[key] = int(val_str)
                    except ValueError:
                        current_table[key] = val_str

        return data
