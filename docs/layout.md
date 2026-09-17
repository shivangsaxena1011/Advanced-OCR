# Layout Understanding & Reading Order

## Structural Classes

- `title`: Primary document header with dominant font height.
- `heading`: Section demarcations (numbered or title-case short blocks).
- `paragraph`: Body text blocks.
- `list`: Bulleted, numbered, or dash-prefixed items.
- `table`: Grids of aligned row and column tokens.
- `header` / `footer`: Top and bottom page margins.
- `key_value`: Attribute-value associations.

## Multi-Column Topological Reading Order

Rather than blindly sorting bounding boxes strictly by Y-coordinate (which causes zigzag reading between columns), AORL:
1. Detects vertical column gutters via horizontal projection.
2. Identifies spanning blocks (titles, headers) that extend across columns.
3. Reads top spanning blocks first.
4. Traverses Column 1 top-to-bottom.
5. Traverses Column 2 top-to-bottom.
6. Finishes with footer spanning blocks.
