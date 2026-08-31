from nobs_txt.framing import Page, PageLine, strip_framing


def _pages(n: int = 6, header: str = "The Great Book") -> list[Page]:
    pages = []
    for index in range(n):
        pages.append(
            Page(
                lines=[
                    PageLine(header, 10, 20),
                    PageLine(f"Body content line {index}.", 200, 212),
                    PageLine(str(index + 1), 780, 790),
                ],
                height=800,
            )
        )
    return pages


def test_strips_repeated_header_and_page_numbers():
    stripped = strip_framing(_pages())
    for page in stripped:
        texts = [line.text for line in page.lines]
        assert len(texts) == 1
        assert texts[0].startswith("Body content")


def test_keeps_non_repeated_header():
    pages = [Page([PageLine("Only Once", 10, 20), PageLine("Body", 300, 312)], 800)]
    stripped = strip_framing(pages)
    assert [line.text for line in stripped[0].lines] == ["Only Once", "Body"]


def test_page_x_of_y_removed():
    pages = [Page([PageLine("Page 3 of 9", 780, 790), PageLine("Body", 300, 312)], 800)]
    stripped = strip_framing(pages)
    assert [line.text for line in stripped[0].lines] == ["Body"]


def test_middle_short_repeated_line_kept():
    pages = [Page([PageLine("Hi", 400, 410)], 800) for _ in range(6)]
    stripped = strip_framing(pages)
    assert all(line.text == "Hi" for page in stripped for line in page.lines)
