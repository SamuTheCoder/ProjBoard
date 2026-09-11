import { ChevronLeft, ChevronRight } from "lucide-react";

import "./CalendarToolbar.css";

type CalendarToolbarProps = {
    monthLabel: string;

    onToday: () => void;
    onPreviousMonth: () => void;
    onNextMonth: () => void;
};

export function CalendarToolbar({
    monthLabel,
    onToday,
    onPreviousMonth,
    onNextMonth,
}: CalendarToolbarProps) {
    return (
        <div className="calendar-toolbar">
            <div className="calendar-toolbar-navigation">
                <button
                    type="button"
                    className="calendar-today-button"
                    onClick={onToday}
                >
                    Today
                </button>

                <button
                    type="button"
                    className="calendar-nav-button"
                    onClick={onPreviousMonth}
                    aria-label="Previous month"
                >
                    <ChevronLeft size={18} />
                </button>

                <button
                    type="button"
                    className="calendar-nav-button"
                    onClick={onNextMonth}
                    aria-label="Next month"
                >
                    <ChevronRight size={18} />
                </button>

                <h3>{monthLabel}</h3>
            </div>
        </div>
    );
}
