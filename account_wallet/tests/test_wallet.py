# © 2015  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from psycopg2 import IntegrityError

from odoo.tools import mute_logger

from .common import WalletCommon


class TestWallet(WalletCommon):
    def test_wallet_name(self):
        self.assertEqual(
            self.wallet.display_name, self.wallet_type.name + " - " + self.wallet.name
        )

    def test_wallet_anonymous(self):
        # Default Configuration
        self.wallet_type.automatic_nominative_creation = False

        # Credit Wallet
        invoice, wallet = self._create_invoice_credit_wallet(100)

        self.assertEqual(wallet.partner_id.id, False)
        self.assertAlmostEqual(wallet.balance, 100.00, 2)

        # Debit Wallet
        self._create_payment_move_wallet(100, wallet)

        self.assertEqual(wallet.partner_id.id, False)
        self.assertEqual(len(wallet.account_move_line_ids), 2)
        self.assertAlmostEqual(wallet.balance, 0.00, 2)

    def test_wallet_with_partner(self):

        # Forbid anonymous wallet
        self.wallet_type.automatic_nominative_creation = True

        # Credit Wallet
        invoice, wallet = self._create_invoice_credit_wallet(200)

        line = self.env["account.move.line"].search(
            [("move_id", "=", invoice.id), ("credit", "=", 200)]
        )
        self.assertEqual(line.partner_id.id, self.partner.id)
        self.assertEqual(wallet.partner_id.id, self.partner.id)

        # Debit Wallet
        self._create_payment_move_wallet(30, wallet)
        self.assertAlmostEqual(wallet.balance, 170.00, 2)

    def test_wallet_unique(self):
        self.wallet.partner_id = self.partner
        with self.assertRaises(IntegrityError):
            with mute_logger("odoo.sql_db"), self.env.cr.savepoint():
                self.AccountWallet.create(
                    {
                        "wallet_type_id": self.wallet_type.id,
                        "partner_id": self.partner.id,
                    }
                )

        wallet_2 = self.AccountWallet.create(
            {
                "wallet_type_id": self.wallet_type.id,
                "partner_id": self.partner.id,
                "active": False,
            }
        )

        with self.assertRaises(IntegrityError):
            with mute_logger("odoo.sql_db"), self.env.cr.savepoint():
                wallet_2.write({"active": True})

        self.wallet.write({"active": False})

    def test_wallet_credit_note(self):
        partner = self.env["res.partner"].create({"name": "Test Wallet credit_notes"})
        product = self.env["product.product"].search([], limit=1)
        values = {
            "account_wallet_type_id": self.wallet_type.id,
            "amount": 50,
            "partner_id": partner.id,
            "invoice_date": "2022-05-18",
            "product_id": product.id,
        }
        wizard = self.env["wizard.account_move_credit_notes.wallet"].create(values)
        wizard.apply()

        credit_note = self.env["account.move"].search(
            [("partner_id", "=", partner.id), ("move_type", "=", "out_refund")]
        )
        self.assertEqual(credit_note.amount_total, 50)
        self.assertEqual(credit_note.move_type, "out_refund")
        self.assertEqual(credit_note.partner_id, partner)
        self.assertEqual(credit_note.invoice_line_ids[0].product_id, product)
        credit_line = credit_note.line_ids.filtered(lambda l: l.credit > 0)
        self.assertEqual(credit_line.account_id, self.wallet_type.account_id)
        self.assertTrue(credit_line.account_wallet_id)
        wallet = credit_line.account_wallet_id
        self.assertEqual(wallet.balance, 50)
