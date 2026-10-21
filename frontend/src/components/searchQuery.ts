// Matching rule shared by every in-memory list filter: case-insensitive
// substring over the fields a row shows. An empty/whitespace query matches
// everything, so the unfiltered list is just the special case query = "".
//
// Lives next to SearchInput because the box and this contract are one feature:
// the input collects the text, this decides which rows survive it.
export function matchesQuery(query: string, ...fields: (string | number | null | undefined)[]): boolean {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return fields.some(
    (field) => field !== null && field !== undefined && String(field).toLowerCase().includes(needle),
  );
}
