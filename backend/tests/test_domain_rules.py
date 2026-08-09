"""The two rules that stop the system from lying.

Both were discovered during F1A research, not invented: the site labels a closed
process "Processo vigente", and the programme publishes no schedule for some
offerings. Getting either wrong makes GradRadar announce an opportunity that does
not exist, or clear a conflict it cannot actually rule out.
"""

from datetime import date, time

from app.models import AdmissionCycle, AdmissionStage, CourseOffering, CycleStatus

WORK_START, WORK_END = time(8, 0), time(18, 0)


def _cycle(open_on: date | None, close_on: date | None, stages: list[AdmissionStage] | None = None):
    c = AdmissionCycle(applications_open_on=open_on, applications_close_on=close_on)
    c.stages = stages or []
    return c


class TestCycleStatusComesFromDates:
    """The site's own label must never decide status."""

    def test_closed_window_is_not_open_even_when_site_says_vigente(self):
        # The real 2026/2 cycle: label "Processo vigente", window closed in April.
        cycle = _cycle(date(2026, 3, 19), date(2026, 4, 26))
        cycle.site_label = "Processo vigente"
        assert cycle.status_on(date(2026, 8, 8)) is CycleStatus.CONCLUDED

    def test_open_while_inside_the_window(self):
        cycle = _cycle(date(2026, 3, 19), date(2026, 4, 26))
        assert cycle.status_on(date(2026, 4, 1)) is CycleStatus.OPEN

    def test_boundaries_are_inclusive(self):
        cycle = _cycle(date(2026, 3, 19), date(2026, 4, 26))
        assert cycle.status_on(date(2026, 3, 19)) is CycleStatus.OPEN
        assert cycle.status_on(date(2026, 4, 26)) is CycleStatus.OPEN

    def test_announced_before_the_window_opens(self):
        cycle = _cycle(date(2026, 3, 19), date(2026, 4, 26))
        assert cycle.status_on(date(2026, 3, 1)) is CycleStatus.ANNOUNCED

    def test_in_progress_while_stages_still_run(self):
        stages = [AdmissionStage(ordinal=1, name="Análise", result_on=date(2026, 6, 24))]
        cycle = _cycle(date(2026, 3, 19), date(2026, 4, 26), stages)
        assert cycle.status_on(date(2026, 5, 20)) is CycleStatus.IN_PROGRESS

    def test_no_dates_means_expected_not_open(self):
        """A cycle we merely predict must never look like one accepting applications."""
        assert _cycle(None, None).status_on(date(2026, 8, 8)) is CycleStatus.EXPECTED


class TestScheduleConflict:
    def test_unknown_schedule_is_none_not_false(self):
        """'We don't know the time' and 'it does not conflict' are opposite answers."""
        assert CourseOffering().overlaps(WORK_START, WORK_END) is None

    def test_morning_band_conflicts(self):
        o = CourseOffering(starts_at=time(8, 0), ends_at=time(12, 0))
        assert o.overlaps(WORK_START, WORK_END) is True

    def test_afternoon_band_conflicts(self):
        o = CourseOffering(starts_at=time(14, 0), ends_at=time(18, 0))
        assert o.overlaps(WORK_START, WORK_END) is True

    def test_an_evening_offering_would_not_conflict(self):
        """PPGCC publishes none — this guards the rule, not the current data."""
        o = CourseOffering(starts_at=time(19, 0), ends_at=time(23, 0))
        assert o.overlaps(WORK_START, WORK_END) is False

    def test_touching_edges_do_not_overlap(self):
        o = CourseOffering(starts_at=time(18, 0), ends_at=time(22, 0))
        assert o.overlaps(WORK_START, WORK_END) is False
