#!/usr/bin/env python
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2015 Thomas Voegtlin
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from enum import IntEnum

from PyQt5.QtCore import Qt, QPersistentModelIndex, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import QAbstractItemView, QComboBox, QLabel, QMenu

from electrum.i18n import _
from electrum.util import block_explorer_URL, profiler
from electrum.plugin import run_hook
from electrum.ravencoin import is_address
from electrum.wallet import InternalAddressCorruption

from .util import MyTreeView, MONOSPACE_FONT, ColorScheme, webopen, MySortModel


class AssetList(MyTreeView):

    class Columns(IntEnum):
        NAME = 0
        BALANCE = 1
        IPFS = 2
        REISSUABLE = 3
        DIVISIONS = 4

    filter_columns = [Columns.NAME, Columns.BALANCE, Columns.IPFS, Columns.REISSUABLE, Columns.DIVISIONS]

    ROLE_SORT_ORDER = Qt.UserRole + 1000
    ROLE_ASSET_STR = Qt.UserRole + 1001

    def __init__(self, parent):
        super().__init__(parent, self.create_menu,
                         stretch_column=None,
                         editable_columns=[])
        self.wallet = self.parent.wallet
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.std_model = QStandardItemModel(self)
        self.proxy = MySortModel(self, sort_role=self.ROLE_SORT_ORDER)
        self.proxy.setSourceModel(self.std_model)
        self.setModel(self.proxy)
        self.update()
        self.sortByColumn(self.Columns.NAME, Qt.AscendingOrder)
        self.asset_meta = {}

    def refresh_headers(self):
        headers = {
            self.Columns.NAME: _('Name'),
            self.Columns.BALANCE: _('Amount'),
            self.Columns.IPFS: _('Asset Data'),
            self.Columns.REISSUABLE: _('Reissuable'),
            self.Columns.DIVISIONS: _('Divisions'),
        }
        self.update_headers(headers)

    @profiler
    def update(self):
        if self.maybe_defer_update():
            return
        current_asset = self.get_role_data_for_current_item(col=self.Columns.NAME, role=self.ROLE_ASSET_STR)
        addr_list = self.wallet.get_addresses()
        self.proxy.setDynamicSortFilter(False)  # temp. disable re-sorting after every change
        self.std_model.clear()
        self.asset_meta.clear()
        self.refresh_headers()
        set_asset = None

        assets = {} # type: Dict[str, Tuple]
        
        for address in addr_list:
            c, u, x = self.wallet.get_addr_balance(address)
            balance = c + u + x
            for asset, balance in balance.assets.items():
                if asset not in assets:
                    meta = self.wallet.get_asset_meta(asset)


        for address in addr_list:
            c, u, x = self.wallet.get_addr_balance(address)

            balance_text = self.parent.format_amount(balance, whitespaces=True)
            # create item
            if fx and fx.get_fiat_address_config():
                rate = fx.exchange_rate()
                fiat_balance = fx.value_str(balance, rate)
            else:
                fiat_balance = ''
            labels = ['', address, label, balance_text, fiat_balance, "%d"%num]
            address_item = [QStandardItem(e) for e in labels]
            # align text and set fonts
            for i, item in enumerate(address_item):
                item.setTextAlignment(Qt.AlignVCenter)
                if i not in (self.Columns.TYPE, self.Columns.LABEL):
                    item.setFont(QFont(MONOSPACE_FONT))
            self.set_editability(address_item)
            address_item[self.Columns.FIAT_BALANCE].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # setup column 0
            if self.wallet.is_change(address):
                address_item[self.Columns.TYPE].setText(_('change'))
                address_item[self.Columns.TYPE].setBackground(ColorScheme.YELLOW.as_color(True))
            else:
                address_item[self.Columns.TYPE].setText(_('receiving'))
                address_item[self.Columns.TYPE].setBackground(ColorScheme.GREEN.as_color(True))
            address_item[self.Columns.LABEL].setData(address, self.ROLE_ADDRESS_STR)
            address_path = self.wallet.get_address_index(address)
            address_item[self.Columns.TYPE].setData(address_path, self.ROLE_SORT_ORDER)
            address_path_str = self.wallet.get_address_path_str(address)
            if address_path_str is not None:
                address_item[self.Columns.TYPE].setToolTip(address_path_str)
            address_item[self.Columns.FIAT_BALANCE].setData(balance, self.ROLE_SORT_ORDER)
            # setup column 1
            if self.wallet.is_frozen_address(address):
                address_item[self.Columns.ADDRESS].setBackground(ColorScheme.BLUE.as_color(True))
            if address in addresses_beyond_gap_limit:
                address_item[self.Columns.ADDRESS].setBackground(ColorScheme.RED.as_color(True))
            # add item
            count = self.std_model.rowCount()
            self.std_model.insertRow(count, address_item)
            address_idx = self.std_model.index(count, self.Columns.LABEL)
            if address == current_asset:
                set_asset = QPersistentModelIndex(address_idx)
        self.set_current_idx(set_asset)
        self.filter()
        self.proxy.setDynamicSortFilter(True)

    def create_menu(self, position):
        from electrum.wallet import Multisig_Wallet
        is_multisig = isinstance(self.wallet, Multisig_Wallet)
        can_delete = self.wallet.can_delete_address()
        selected = self.selected_in_column(self.Columns.ADDRESS)
        if not selected:
            return
        multi_select = len(selected) > 1
        addrs = [self.item_from_index(item).text() for item in selected]
        menu = QMenu()
        if not multi_select:
            idx = self.indexAt(position)
            if not idx.isValid():
                return
            item = self.item_from_index(idx)
            if not item:
                return
            addr = addrs[0]
            addr_column_title = self.std_model.horizontalHeaderItem(self.Columns.LABEL).text()
            addr_idx = idx.sibling(idx.row(), self.Columns.LABEL)
            self.add_copy_menu(menu, idx)
            menu.addAction(_('Details'), lambda: self.parent.show_address(addr))
            persistent = QPersistentModelIndex(addr_idx)
            menu.addAction(_("Edit {}").format(addr_column_title), lambda p=persistent: self.edit(QModelIndex(p)))
            #menu.addAction(_("Request payment"), lambda: self.parent.receive_at(addr))
            if self.wallet.can_export():
                menu.addAction(_("Private key"), lambda: self.parent.show_private_key(addr))
            if not is_multisig and not self.wallet.is_watching_only():
                menu.addAction(_("Sign/verify message"), lambda: self.parent.sign_verify_message(addr))
                menu.addAction(_("Encrypt/decrypt message"), lambda: self.parent.encrypt_message(addr))
            if can_delete:
                menu.addAction(_("Remove from wallet"), lambda: self.parent.remove_address(addr))
            addr_URL = block_explorer_URL(self.config, 'addr', addr)
            if addr_URL:
                menu.addAction(_("View on block explorer"), lambda: webopen(addr_URL))

            if not self.wallet.is_frozen_address(addr):
                menu.addAction(_("Freeze"), lambda: self.parent.set_frozen_state_of_addresses([addr], True))
            else:
                menu.addAction(_("Unfreeze"), lambda: self.parent.set_frozen_state_of_addresses([addr], False))

        coins = self.wallet.get_spendable_coins(addrs)
        if coins:
            menu.addAction(_("Spend from"), lambda: self.parent.utxo_list.set_spend_list(coins))

        run_hook('receive_menu', menu, addrs, self.wallet)
        menu.exec_(self.viewport().mapToGlobal(position))

    def place_text_on_clipboard(self, text: str, *, title: str = None) -> None:
        if is_address(text):
            try:
                self.wallet.check_address_for_corruption(text)
            except InternalAddressCorruption as e:
                self.parent.show_error(str(e))
                raise
        super().place_text_on_clipboard(text, title=title)

    def get_edit_key_from_coordinate(self, row, col):
        return None

    # We don't edit anything here
    def on_edited(self, idx, edit_key, *, text):
        pass
