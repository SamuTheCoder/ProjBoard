import { useMemo, useState } from "react";

import type { TaskResponse } from "../../types/task";

import { CalendarToolbar } from "../CalendarToolbar/CalendarToolbar";
import { CalendarDayCell } from "../CalendarDayCell/CalendarDayCell";
import { CalendarSidebar } from "../CalendarSidebar/CalendarSidebar";

import "./ProjectCalendar.css";

type ProjectCalendarProps = {
    tasks: TaskResponse[];
    onTaskClick: (task: TaskResponse) => void;
};

const WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function startOfDay(date: Date): Date {
    return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function isSameDay(first: Date, second: Date): boolean {
    return (
        first.getFullYear() === second.getFullYear() &&
        first.getMonth() === second.getMonth() &&
        first.getDate() === second.getDate()
    );
}

function taskDeadlineDate(task: TaskResponse): Date | null {
    if (!task.task_deadline) {
        return null;
    }

    return new Date(task.task_deadline);
}

function generateCalendarDates(month: Date): Date[] {
    const year = month.getFullYear();
    const monthIndex = month.getMonth();

    const firstDayOfMonth = new Date(year, monthIndex, 1);

    /*
     * JS:
     * Sunday = 0
     * Monday = 1
     *
     * We want Monday to be index 0.
     */
    const daysSinceMonday = (firstDayOfMonth.getDay() + 6) % 7;

    const calendarStart = new Date(year, monthIndex, 1 - daysSinceMonday);

    return Array.from({ length: 42 }, (_, index) => {
        const date = new Date(calendarStart);

        date.setDate(calendarStart.getDate() + index);

        return date;
    });
}

export function ProjectCalendar({ tasks, onTaskClick }: ProjectCalendarProps) {
    const today = new Date();

    const [currentMonth, setCurrentMonth] = useState(
        new Date(today.getFullYear(), today.getMonth(), 1),
    );

    const [selectedDate, setSelectedDate] = useState(startOfDay(today));

    /*
     * Calendar only cares about tasks
     * that actually have deadlines.
     */
    const tasksWithDeadlines = useMemo(
        () => tasks.filter((task) => task.task_deadline !== null),
        [tasks],
    );

    const calendarDates = useMemo(
        () => generateCalendarDates(currentMonth),
        [currentMonth],
    );

    const selectedDayTasks = useMemo(
        () =>
            tasksWithDeadlines
                .filter((task) => {
                    const deadline = taskDeadlineDate(task);

                    return (
                        deadline !== null && isSameDay(deadline, selectedDate)
                    );
                })
                .sort((first, second) => {
                    return (
                        new Date(first.task_deadline!).getTime() -
                        new Date(second.task_deadline!).getTime()
                    );
                }),
        [tasksWithDeadlines, selectedDate],
    );

    const upcomingTasks = useMemo(() => {
        const startToday = startOfDay(new Date()).getTime();

        return tasksWithDeadlines
            .filter((task) => {
                const deadline = taskDeadlineDate(task);

                return deadline !== null && deadline.getTime() >= startToday;
            })
            .sort(
                (first, second) =>
                    new Date(first.task_deadline!).getTime() -
                    new Date(second.task_deadline!).getTime(),
            )
            .slice(0, 5);
    }, [tasksWithDeadlines]);

    const monthLabel = currentMonth.toLocaleDateString(undefined, {
        month: "long",
        year: "numeric",
    });

    function getTasksForDate(date: Date): TaskResponse[] {
        return tasksWithDeadlines.filter((task) => {
            const deadline = taskDeadlineDate(task);

            return deadline !== null && isSameDay(deadline, date);
        });
    }

    function handlePreviousMonth() {
        setCurrentMonth(
            (current) =>
                new Date(current.getFullYear(), current.getMonth() - 1, 1),
        );
    }

    function handleNextMonth() {
        setCurrentMonth(
            (current) =>
                new Date(current.getFullYear(), current.getMonth() + 1, 1),
        );
    }

    function handleToday() {
        const now = new Date();

        setCurrentMonth(new Date(now.getFullYear(), now.getMonth(), 1));

        setSelectedDate(startOfDay(now));
    }

    function handleSelectDate(date: Date) {
        setSelectedDate(startOfDay(date));

        /*
         * Clicking one of the faded days
         * belonging to another month moves
         * the calendar to that month.
         */
        if (
            date.getMonth() !== currentMonth.getMonth() ||
            date.getFullYear() !== currentMonth.getFullYear()
        ) {
            setCurrentMonth(new Date(date.getFullYear(), date.getMonth(), 1));
        }
    }

    return (
        <section className="project-calendar">
            <div className="project-calendar-main">
                <div className="calendar-container">
                    <CalendarToolbar
                        monthLabel={monthLabel}
                        onToday={handleToday}
                        onPreviousMonth={handlePreviousMonth}
                        onNextMonth={handleNextMonth}
                    />

                    <div className="calendar-week-header">
                        {WEEK_DAYS.map((day) => (
                            <div key={day}>{day}</div>
                        ))}
                    </div>

                    <div className="calendar-grid">
                        {calendarDates.map((date) => {
                            const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;

                            return (
                                <CalendarDayCell
                                    key={key}
                                    date={date}
                                    tasks={getTasksForDate(date)}
                                    isCurrentMonth={
                                        date.getMonth() ===
                                            currentMonth.getMonth() &&
                                        date.getFullYear() ===
                                            currentMonth.getFullYear()
                                    }
                                    isToday={isSameDay(date, today)}
                                    isSelected={isSameDay(date, selectedDate)}
                                    onSelect={handleSelectDate}
                                    onTaskClick={onTaskClick}
                                />
                            );
                        })}
                    </div>
                </div>

                <CalendarSidebar
                    selectedDate={selectedDate}
                    selectedTasks={selectedDayTasks}
                    upcomingTasks={upcomingTasks}
                    onTaskClick={onTaskClick}
                />
            </div>
        </section>
    );
}
