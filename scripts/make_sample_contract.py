"""Generate a complete, multi-page fictional Service Agreement PDF.

Run from the project root:
    python scripts/make_sample_contract.py
"""
import io
from pathlib import Path

import pymupdf

OUTPUT = Path(__file__).resolve().parent.parent / "data" / "documents" / "sample_contract.pdf"
FOOTER = "Service Agreement - Northstar Analytics & Blue Oak Solutions"

CSS = """
body { font-family: serif; font-size: 10pt; line-height: 1.3; }
h1 { font-size: 18pt; text-align: center; margin-bottom: 2pt; }
h2 { font-size: 11.5pt; margin-top: 11pt; margin-bottom: 3pt; }
p { margin-top: 0; margin-bottom: 5pt; }
.sub { text-align: center; font-style: italic; color: #555555; margin-bottom: 8pt; }
.item { margin-left: 16pt; margin-top: 0; margin-bottom: 2pt; }
td, th { padding: 3pt 8pt; border: 0.5pt solid #999999; }
th { background-color: #eeeeee; text-align: left; }
"""

# (heading, [paragraphs]); a paragraph starting with "- " is rendered as a list item
CLAUSES = [
    ("1. Scope of Services", [
        "The Service Provider agrees to design, develop, test, and deliver a custom business analytics dashboard for the Client.",
        "The project shall include:",
        "- Development of an interactive analytics dashboard.",
        "- Integration with the Client's existing business data.",
        "- Implementation of reporting and visualization features.",
        "- Testing and deployment of the final application.",
        "- Basic technical documentation and handover.",
        "Any additional services outside this scope must be mutually agreed upon in writing.",
    ]),
    ("2. Project Timeline", [
        "The project shall follow the following schedule:",
        "TABLE",
        "The Service Provider shall notify the Client promptly of any anticipated delays. Any extension to the project timeline must be approved in writing by both Parties.",
    ]),
    ("3. Contract Value and Payment Terms", [
        "The total contract value shall be INR 240,000 (Rupees Two Lakh Forty Thousand Only). Payments shall be made according to the following schedule:",
        "- 30% advance payment upon signing: INR 72,000.",
        "- 40% upon prototype approval: INR 96,000.",
        "- 30% upon final delivery: INR 72,000.",
        "All payments shall be made within seven business days of receiving the corresponding invoice. Applicable taxes shall be charged separately as required by law.",
    ]),
    ("4. Client Responsibilities", [
        "The Client shall:",
        "- Provide timely access to relevant business data, systems, and personnel.",
        "- Nominate a single point of contact for approvals and feedback.",
        "- Review each deliverable and provide written feedback within five business days.",
        "- Ensure that it holds all rights necessary to share the data it provides.",
        "Delays caused by the Client's failure to meet these responsibilities may extend the project timeline by a corresponding period.",
    ]),
    ("5. Confidentiality", [
        "Each Party shall keep confidential all non-public information received from the other Party in connection with this Agreement, and shall use it solely for the purposes of this Agreement. Confidential information does not include information that is publicly available through no fault of the receiving Party, was already lawfully known to the receiving Party, or is independently developed without use of the disclosing Party's information. A Party may disclose confidential information where required by law, provided it gives the other Party prompt written notice where legally permitted.",
        "The obligations in this clause continue for three years after the termination or completion of this Agreement.",
    ]),
    ("6. Acceptance and Warranty", [
        "The Client shall have ten business days from each delivery to test the deliverable and notify the Service Provider in writing of any material defects. Deliverables not rejected within that period shall be deemed accepted.",
        "The Service Provider warrants that the final deliverable will conform to the agreed scope for ninety days after final delivery and shall correct any material non-conformity reported within that period at no additional charge. This warranty does not cover defects caused by modifications made by the Client or by third parties.",
    ]),
    ("7. Data Protection and Security", [
        "The Service Provider shall:",
        "1. Use Client data only for performing the agreed services.",
        "2. Implement reasonable technical and organizational security measures.",
        "3. Restrict access to Client data to authorized personnel.",
        "4. Notify the Client within 48 hours of becoming aware of a confirmed unauthorized disclosure of Client data.",
        "Upon completion or termination of the project, the Service Provider shall return or securely delete Client data, subject to applicable legal retention requirements.",
    ]),
    ("8. Intellectual Property Rights", [
        "Upon receipt of all outstanding payments, all project-specific deliverables developed exclusively for the Client shall become the intellectual property of the Client. The Service Provider shall retain ownership of its pre-existing software, tools, frameworks, libraries, and general-purpose development methodologies. The Service Provider grants the Client a perpetual, non-exclusive license to use any pre-existing components incorporated into the deliverables as necessary for operating the delivered solution.",
    ]),
    ("9. Termination", [
        "Either Party may terminate this Agreement by providing 30 days' written notice. Either Party may terminate the Agreement immediately if the other Party commits a material breach and fails to remedy the breach within 15 days of receiving written notice. Upon termination:",
        "- The Client shall pay for services satisfactorily performed up to the termination date.",
        "- The Service Provider shall return Client-owned materials.",
        "- Confidentiality and intellectual property obligations shall survive as applicable.",
    ]),
    ("10. Force Majeure", [
        "Neither Party shall be liable for delays or failures caused by events beyond its reasonable control, including natural disasters, war, government restrictions, widespread network failures, or other unforeseeable events. The affected Party must notify the other Party within seven days of becoming aware of the event. If the force majeure event continues for more than 60 consecutive days, either Party may terminate this Agreement by written notice.",
    ]),
    ("11. Limitation of Liability", [
        "Except for the exclusions stated below, the total aggregate liability of either Party arising out of or relating to this Agreement shall not exceed the total contract value of INR 240,000. Neither Party shall be liable for indirect, incidental, special, or consequential damages, including loss of profits or business opportunities. The limitations in this clause shall not apply to:",
        "- Fraud or willful misconduct.",
        "- Breach of confidentiality obligations.",
        "- Unauthorized disclosure or misuse of Client data.",
        "- Intellectual property infringement.",
    ]),
    ("12. Governing Law and Jurisdiction", [
        "This Agreement shall be governed by and interpreted in accordance with the laws of India. The courts located in Jaipur, Rajasthan, shall have exclusive jurisdiction over disputes arising from this Agreement.",
    ]),
    ("13. Entire Agreement", [
        "This Agreement represents the entire understanding between the Parties and supersedes all prior discussions and agreements, whether written or oral, relating to its subject matter. Any amendment to this Agreement must be made in writing and signed by both Parties.",
    ]),
]


def build_html() -> str:
    parts = [
        "<h1>SERVICE AGREEMENT</h1>",
        "<p class='sub'>Fictional Sample Document \u2013 For AI Testing Purposes Only</p>",
        "<p><b>Agreement Date: 1 October 2026</b></p>",
        "<p>This Service Agreement (\"Agreement\") is entered into between:</p>",
        "<p class='item'>Northstar Analytics Pvt Ltd, hereinafter referred to as the \"Client\", having its registered office in Jaipur, Rajasthan, India; AND</p>",
        "<p class='item'>Blue Oak Solutions LLP, hereinafter referred to as the \"Service Provider\", having its registered office in Bengaluru, Karnataka, India.</p>",
        "<p>The Client and the Service Provider shall collectively be referred to as the \"Parties\".</p>",
    ]

    for heading, paragraphs in CLAUSES:
        parts.append(f"<h2>{heading}</h2>")

        for paragraph in paragraphs:
            if paragraph == "TABLE":
                parts.append(
                    "<table><tr><th>Milestone</th><th>Deadline</th></tr>"
                    "<tr><td>Project commencement</td><td>5 October 2026</td></tr>"
                    "<tr><td>Prototype delivery</td><td>20 October 2026</td></tr>"
                    "<tr><td>Final delivery</td><td>15 November 2026</td></tr></table>"
                    "<p></p>"
                )
            elif paragraph.startswith("- "):
                parts.append(f"<p class='item'>\u2022 {paragraph[2:]}</p>")
            elif paragraph[:2] in {"1.", "2.", "3.", "4."} and paragraph[2] == " ":
                parts.append(f"<p class='item'>{paragraph}</p>")
            else:
                parts.append(f"<p>{paragraph}</p>")

    return "<body>" + "".join(parts) + "</body>"


def render() -> bytes:
    story = pymupdf.Story(html=build_html(), user_css=CSS)
    buffer = io.BytesIO()
    writer = pymupdf.DocumentWriter(buffer)

    mediabox = pymupdf.paper_rect("a4")
    content_area = mediabox + (54, 54, -54, -72)

    more = True
    while more:
        device = writer.begin_page(mediabox)
        more, _ = story.place(content_area)
        story.draw(device)
        writer.end_page()

    writer.close()
    return buffer.getvalue()


def add_footers(pdf_bytes: bytes) -> pymupdf.Document:
    document = pymupdf.open("pdf", pdf_bytes)
    total = len(document)

    for page in document:
        y = page.rect.height - 40
        page_label = f"Page {page.number + 1} of {total}"
        label_width = pymupdf.get_text_length(page_label, fontsize=8)

        page.insert_text((54, y), FOOTER, fontsize=8, color=(0.4, 0.4, 0.4))
        page.insert_text(
            (page.rect.width - 54 - label_width, y),
            page_label, fontsize=8, color=(0.4, 0.4, 0.4)
        )

    return document


if __name__ == "__main__":
    document = add_footers(render())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(OUTPUT))
    print(f"Wrote {OUTPUT} ({len(document)} pages)")