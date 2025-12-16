// utils/parse.ts
export function parseMaybeJSON(val: any) {
  if (typeof val !== "string") return val

  try {
    // Python dict → JSON
    const fixed = val
      .replace(/'/g, '"')
      .replace("None", "null")
    return JSON.parse(fixed)
  } catch {
    return val
  }
}

export function parseNumber(val: any): number {
  const n = Number(val)
  return isNaN(n) ? 0 : n
}
