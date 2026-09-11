import { CalendarClock } from "lucide-react";

import type { TaskResponse } from "../../types/task";

import "./CalendarSidebar.css";

type CalendarSidebarProps = {
    selectedDate: Date;

    selectedTasks: TaskResponse[];
    upcomingTasks: TaskResponse[];

    onTaskClick: (task: TaskResponse) => void;
};

function formatSelectedDate(date: Date) {
    return date.toLocaleDateString(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
        year: "numeric",
    });
}

function formatDeadline(date: string | null) {
    if (!date) {
        return "No deadline";
    }

    return new Date(date).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
    });
}

export function CalendarSidebar({
    selectedDate,
    selectedTasks,
    upcomingTasks,
    onTaskClick,
}: CalendarSidebarProps) {
    return (
        <aside className="calendar-sidebar">
            <section className="calendar-sidebar-section">
                <div className="calendar-sidebar-heading">
                    <h3>{formatSelectedDate(selectedDate)}</h3>

                    <span>
                        {selectedTasks.length}{" "}
                        {selectedTasks.length === 1 ? "task" : "tasks"}
                    </span>
                </div>

                <div className="calendar-sidebar-tasks">
                    {selectedTasks.length > 0 ? (
                        selectedTasks.map((task) => (
                            <button
                                type="button"
                                className="calendar-sidebar-task"
                                key={task.task_id}
                                onClick={() => onTaskClick(task)}
                            >
                                <span
                                    className={`calendar-sidebar-dot priority-${task.priority}`}
                                />

                                <div>
                                    <strong>{task.task_name}</strong>

                                    <span>P{task.priority}</span>
                                </div>
                            </button>
                        ))
                    ) : (
                        <p className="calendar-sidebar-empty">
                            No tasks due this day.
                        </p>
                    )}
                </div>
            </section>

            <section className="calendar-sidebar-section upcoming">
                <div className="calendar-sidebar-heading">
                    <h3>Upcoming</h3>
                    <CalendarClock size={18} />
                </div>

                <div className="calendar-sidebar-tasks">
                    {upcomingTasks.map((task) => (
                        <button
                            type="button"
                            className="calendar-upcoming-task"
                            key={task.task_id}
                            onClick={() => onTaskClick(task)}
                        >
                            <span
                                className={`calendar-sidebar-dot priority-${task.priority}`}
                            />

                            <div>
                                <strong>{task.task_name}</strong>

                                <span>P{task.priority}</span>
                            </div>

                            <time>{formatDeadline(task.task_deadline)}</time>
                        </button>
                    ))}

                    {upcomingTasks.length === 0 && (
                        <p className="calendar-sidebar-empty">
                            No upcoming tasks.
                        </p>
                    )}
                </div>
            </section>
        </aside>
    );
}
