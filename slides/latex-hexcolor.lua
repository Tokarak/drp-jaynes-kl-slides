-- KaTeX accepts \textcolor{#d55e00}{...}; LaTeX's xcolor needs \textcolor[HTML]{D55E00}{...}.
-- Rewrite hex colours in maths for LaTeX output only (HTML/revealjs untouched).
if not FORMAT:match("latex") then return {} end

local function fix(s)
  return (s:gsub("\\(%a*color){#(%x%x%x%x%x%x)}", function(cmd, hex)
    return "\\" .. cmd .. "[HTML]{" .. hex:upper() .. "}"
  end))
end

return {
  Math = function(m) m.text = fix(m.text); return m end,
  RawInline = function(r) if r.format:match("tex") then r.text = fix(r.text) end; return r end,
  RawBlock = function(r) if r.format:match("tex") then r.text = fix(r.text) end; return r end,
}
