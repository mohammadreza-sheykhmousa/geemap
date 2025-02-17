#!/usr/bin/env python

"""Tests for `map_widgets` module."""


import unittest
from unittest.mock import patch, MagicMock, ANY
import geemap
from geemap.toolbar import Toolbar, main_tools, extra_tools


class TestToolbar(unittest.TestCase):
    """Tests for the Toolbar class in the `toolbar` module."""

    def setUp(self) -> None:
        self.callback_calls = 0
        self.last_called_with_selected = None
        self.item = Toolbar.Item(
            icon="info", tooltip="dummy item", callback=self.dummy_callback
        )
        self.no_reset_item = Toolbar.Item(
            icon="question",
            tooltip="no reset item",
            callback=self.dummy_callback,
            reset=False,
        )
        return super().setUp()

    def tearDown(self) -> None:
        patch.stopall()
        return super().tearDown()

    def dummy_callback(self, m, selected):
        del m
        self.last_called_with_selected = selected
        self.callback_calls += 1

    def test_no_tools_throws(self):
        map = geemap.Map(ee_initialize=False)
        self.assertRaises(ValueError, Toolbar, map, [], [])

    def test_only_main_tools_exist_if_no_extra_tools(self):
        map = geemap.Map(ee_initialize=False)
        toolbar = Toolbar(map, [self.item], [])
        self.assertIsNone(toolbar.toggle_widget)
        self.assertEqual(len(toolbar.all_widgets), 1)
        self.assertEqual(toolbar.all_widgets[0].icon, "info")
        self.assertEqual(toolbar.all_widgets[0].tooltip, "dummy item")
        self.assertFalse(toolbar.all_widgets[0].value)
        self.assertEqual(toolbar.num_rows_collapsed, 1)
        self.assertEqual(toolbar.num_rows_expanded, 1)

    def test_all_tools_and_toggle_exist_if_extra_tools(self):
        map = geemap.Map(ee_initialize=False)
        toolbar = Toolbar(map, [self.item], [self.no_reset_item])
        self.assertIsNotNone(toolbar.toggle_widget)
        self.assertEqual(len(toolbar.all_widgets), 3)
        self.assertEqual(toolbar.all_widgets[2].icon, "question")
        self.assertEqual(toolbar.all_widgets[2].tooltip, "no reset item")
        self.assertFalse(toolbar.all_widgets[2].value)
        self.assertEqual(toolbar.num_rows_collapsed, 1)
        self.assertEqual(toolbar.num_rows_expanded, 1)

    def test_has_correct_number_of_rows(self):
        map = geemap.Map(ee_initialize=False)
        toolbar = Toolbar(map, [self.item, self.item], [self.item, self.item])
        self.assertEqual(toolbar.num_rows_collapsed, 1)
        self.assertEqual(toolbar.num_rows_expanded, 2)

    def test_toggle_expands_and_collapses(self):
        map = geemap.Map(ee_initialize=False)
        toolbar = Toolbar(map, [self.item], [self.no_reset_item])
        self.assertEqual(len(toolbar.grid.children), 2)
        self.assertIsNotNone(toolbar.toggle_widget)
        toggle = toolbar.all_widgets[1]
        self.assertEqual(toggle.icon, "plus")
        self.assertEqual(toggle.tooltip, "Expand toolbar")

        # Expand
        toggle.value = True
        self.assertEqual(len(toolbar.grid.children), 3)
        self.assertEqual(toggle.icon, "minus")
        self.assertEqual(toggle.tooltip, "Collapse toolbar")
        # After expanding, button is unselected.
        self.assertFalse(toggle.value)

        # Collapse
        toggle.value = True
        self.assertEqual(len(toolbar.grid.children), 2)
        self.assertEqual(toggle.icon, "plus")
        self.assertEqual(toggle.tooltip, "Expand toolbar")
        # After collapsing, button is unselected.
        self.assertFalse(toggle.value)

    def test_triggers_callbacks(self):
        map = geemap.Map(ee_initialize=False)
        toolbar = Toolbar(map, [self.item, self.no_reset_item])
        self.assertIsNone(self.last_called_with_selected)

        # Select first tool, which resets.
        toolbar.all_widgets[0].value = True
        self.assertFalse(self.last_called_with_selected)  # was reset by callback
        self.assertEqual(self.callback_calls, 2)
        self.assertFalse(toolbar.all_widgets[0].value)

        # Select second tool, which does not reset.
        toolbar.all_widgets[1].value = True
        self.assertTrue(self.last_called_with_selected)
        self.assertEqual(self.callback_calls, 3)
        self.assertTrue(toolbar.all_widgets[1].value)
