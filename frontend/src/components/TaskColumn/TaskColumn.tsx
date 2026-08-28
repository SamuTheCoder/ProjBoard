import type { ReactNode } from "react";
import "./TaskColumn.css";

type TaskColumnProps = {
    title: string;
    count: number;
    children: ReactNode;
    onAddTask?: () => void;
};

export function TaskColumn({
    title,
    count,
    children,
    onAddTask,
}: TaskColumnProps) {
    return (
        <section className="task-column">
            <div className="task-column-header">
                <h3>{title}</h3>
                <span>{count}</span>
            </div>

            <div className="task-column-content">{children}</div>

            {onAddTask && (
                <button
                    className="task-column-add"
                    type="button"
                    onClick={onAddTask}
                >
                    + Add Task
                </button>
            )}
        </section>
    );
}
