from .common import DocumentsSearchCommon


class TestDocumentsSearch(DocumentsSearchCommon):
    def test_documents_search(self):
        """Unit Test document search."""
        documents_search_object = self.env["dms.search"]

        # --------------------------------------------------
        # Case1: Search the document in attachments with the code and find it.
        # --------------------------------------------------

        attachment_img = self.env.ref("dms.ir_attachment_img")
        documents_search_code = documents_search_object.sudo().create(
            {"name": "text arabic - Demo Image"}
        )
        documents_search_code.button_filter_search()
        self.assertIn(
            attachment_img.id,
            documents_search_code.document_ids.ids,
            "The search result should contain the image 'text_arabic.png'.",
        )

        # --------------------------------------------------
        # Case2: Search the document in attachments with the code and not find it.
        # --------------------------------------------------

        documents_search_code = documents_search_object.sudo().create({"code": "00004"})
        documents_search_code.button_filter_search()
        self.assertEqual(
            documents_search_code.document_ids.ids,
            [],
            "The search result should be empty.",
        )

        # --------------------------------------------------
        # Case3 : Search the document with the type_id and find it.
        # --------------------------------------------------

        attachment_pdf = self.env.ref("dms.ir_attachment_pdf")
        attachment_type = self.env.ref("dms.ir_attachment_type1")
        documents_search_code = documents_search_object.sudo().create(
            {"document_type_id": attachment_type.id}
        )
        documents_search_code.button_filter_search()
        self.assertIn(
            attachment_pdf.id,
            documents_search_code.document_ids.ids,
            "The search result should contain the image 'text_arabic.pdf'.",
        )
