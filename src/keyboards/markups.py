from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

import models
from . import buttons

__all__ = (
    'UpdateStatisticsReportMarkup',
    'MainMenuMarkup',
    'StatisticsReportsMarkup',
    'RegionsMarkup',
    'SettingsMarkup',
    'UnitsMarkup',
)


class MainMenuMarkup(ReplyKeyboardMarkup):

    def __init__(self):
        super().__init__(row_width=1, resize_keyboard=True)
        self.add(
            buttons.StatisticsReportsButton(),
            buttons.SettingsButton(),
        )


class UpdateStatisticsReportMarkup(InlineKeyboardMarkup):

    def __init__(self, report_name: str):
        super().__init__()
        self.add(
            buttons.UpdateStatisticsButton(report_name),
        )


class StatisticsReportsMarkup(InlineKeyboardMarkup):

    def __init__(self):
        super().__init__(row_width=1)
        self.add(*(buttons.ShowStatisticsButton(statistics_type)
                   for statistics_type in models.database.StatisticsReportType))


class SettingsMarkup(InlineKeyboardMarkup):

    def __init__(self):
        super().__init__(row_width=1)
        self.add(*(buttons.ReportSettingsButton(report)
                   for report in models.database.ReportType))


class RegionsMarkup(InlineKeyboardMarkup):

    def __init__(self, report_type: str, regions: str):
        super().__init__()
        self.add(*(buttons.ChooseRegionButton(report_type, region) for region in regions))


class UnitsMarkup(InlineKeyboardMarkup):

    def __init__(self, report_type: str, region: str, enabled_unit_ids: Iterable[int],
                 all_units: Iterable[models.Unit]):
        super().__init__(row_width=2)
        self.__report_type = report_type
        self.__region = region
        self.__all_units = all_units
        self.__enabled_unit_ids = set(enabled_unit_ids)

        self.__add_unit_operations()
        self.__add_batch_operations()

    @property
    def __all_unit_ids(self) -> set[int]:
        return {unit.id for unit in self.__all_units}

    @property
    def __disabled_unit_ids(self) -> set[int]:
        return self.__all_unit_ids - self.__enabled_unit_ids

    def __add_unit_operations(self) -> None:
        for unit in self.__all_units:
            is_unit_enabled = unit.id in self.__enabled_unit_ids
            button = buttons.SwitchUnitStatusButton(self.__report_type, self.__region,
                                                    unit.id, unit.name, is_unit_enabled)
            self.insert(button)

    def __add_batch_operations(self) -> None:
        row = []
        if any(self.__disabled_unit_ids):
            row.append(buttons.EnableAllUnitsByRegionButton(self.__report_type, self.__region))
        if any(self.__enabled_unit_ids):
            row.append(buttons.DisableAllUnitsByRegionButton(self.__report_type, self.__region))
        self.row(*row)
