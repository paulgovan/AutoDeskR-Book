-- Fix bare `class` attributes (e.g. <div class>) that are valid HTML5
-- but invalid XML/XHTML, causing EPUB validators to reject the file.

local function fix_html(text)
  -- Match `class` followed by whitespace, `>`, or `/` but not `=`
  return text:gsub('(%s)class([%s>/])', '%1class=""%2')
end

function RawBlock(el)
  if el.format == "html" or el.format == "html5" then
    el.text = fix_html(el.text)
    return el
  end
end

function RawInline(el)
  if el.format == "html" or el.format == "html5" then
    el.text = fix_html(el.text)
    return el
  end
end
