# Copyright 2015-2021 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Wallet",
    "version": "14.0.2.0.0",
    "author": "Odoo Community Association (OCA), ACSONE SA/NV",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/wallet",
    "depends": [
        "account",
    ],
    "data": [
        "security/security.xml",
        "security/wallet_base_security.xml",
        "views/account_wallet.xml",
        "views/account_wallet_type.xml",
        "views/account_move_line.xml",
        "views/account_move.xml",
        "views/res_partner.xml",
        "wizards/wizard_account_move_credit_notes_wallet.xml",
        "views/wallet_settings.xml",
    ],
    "license": "AGPL-3",
    "post_init_hook": "post_init_hook",
}
