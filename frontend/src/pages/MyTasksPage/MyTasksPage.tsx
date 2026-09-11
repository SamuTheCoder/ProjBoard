import { useEffect, useMemo, useState } from "react";

import {
    CircleCheckBig,
    Eye,
    ListTodo,
    PenLine,
    UserRound,
} from "lucide-react";

import { Navbar } from "../../components/Navbar/Navbar";
import { StatCard } from "../../components/StatCard/StatCard";
import { TaskFilters } from "../../components/TaskFilters/TaskFilters";
import type { TaskFilterState } from "../../components/TaskFilters/TaskFilters";

import {
    TaskTableRow,
    type TaskRole,
} from "../../components/TaskTableRow/TaskTableRow";

import { TaskDetailsPanel } from "../../components/TaskDetailsPanel/TaskDetailsPanel";
import { ErrorToast } from "../../components/ErrorToast/ErrorToast";

import { getCurrentUser } from "../../api/user";
import { getProjects } from "../../api/project";
import { getProjectTasks, updateTask } from "../../api/task";
import { getProjectMembers } from "../../api/member";
import { getApiErrorMessage } from "../../api/errors";

import type { TaskResponse, TaskUpdate } from "../../types/task";

import type { ProjectMemberResponse } from "../../types/member";
import type { UserResponse } from "../../types/auth";
import type { ProjectResponse } from "../../types/project";

import "./MyTasksPage.css";

type MyTaskView = {
    task: TaskResponse;
    projectName: string;
    role: TaskRole;
};

type SummaryFilter = "all" | "assigned" | "created" | "reviewing" | "completed";

const initialFilters: TaskFilterState = {
    status: "all",
    priority: "all",
    projectId: "all",
    role: "all",
};

function taskBelongsToUser(task: TaskResponse, userId: number): boolean {
    return (
        task.created_by === userId ||
        task.assignee_id === userId ||
        task.reviewer_id === userId
    );
}

function getTaskRole(task: TaskResponse, userId: number): TaskRole {
    if (task.reviewer_id === userId) {
        return "reviewer";
    }

    if (task.assignee_id === userId) {
        return "assignee";
    }

    return "creator";
}

export function MyTasksPage() {
    const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);

    const [projects, setProjects] = useState<ProjectResponse[]>([]);

    const [tasks, setTasks] = useState<MyTaskView[]>([]);

    const [selectedTask, setSelectedTask] = useState<TaskResponse | null>(null);

    const [selectedTaskMembers, setSelectedTaskMembers] = useState<
        ProjectMemberResponse[]
    >([]);

    const [filters, setFilters] = useState<TaskFilterState>(initialFilters);

    const [summaryFilter, setSummaryFilter] = useState<SummaryFilter>("all");

    const [error, setError] = useState("");

    const [loading, setLoading] = useState(true);

    const [page, setPage] = useState(1);

    const [isTaskPanelClosing, setIsTaskPanelClosing] = useState(false);

    const rowsPerPage = 7;

    /*
     * Load current user + projects + all tasks
     */
    useEffect(() => {
        async function loadMyTasks() {
            setLoading(true);
            setError("");

            try {
                const [userData, projectData] = await Promise.all([
                    getCurrentUser(),
                    getProjects(),
                ]);

                setCurrentUser(userData);
                setProjects(projectData);

                const projectTaskLists = await Promise.all(
                    projectData.map(async (project) => {
                        const projectTasks = await getProjectTasks(
                            project.project_id,
                        );

                        return projectTasks
                            .filter((task) =>
                                taskBelongsToUser(task, userData.user_id),
                            )
                            .map(
                                (task): MyTaskView => ({
                                    task,
                                    projectName: project.project_name,
                                    role: getTaskRole(task, userData.user_id),
                                }),
                            );
                    }),
                );

                setTasks(projectTaskLists.flat());
            } catch (error) {
                setError(getApiErrorMessage(error));
            } finally {
                setLoading(false);
            }
        }

        loadMyTasks();
    }, []);

    /*
     * Summary counts
     */
    const assignedCount = currentUser
        ? tasks.filter(({ task }) => task.assignee_id === currentUser.user_id)
              .length
        : 0;

    const createdCount = currentUser
        ? tasks.filter(({ task }) => task.created_by === currentUser.user_id)
              .length
        : 0;

    const reviewingCount = currentUser
        ? tasks.filter(({ task }) => task.reviewer_id === currentUser.user_id)
              .length
        : 0;

    const completedCount = tasks.filter(
        ({ task }) => task.status === "done",
    ).length;

    /*
     * Filters
     */
    const filteredTasks = useMemo(() => {
        if (!currentUser) {
            return [];
        }

        return tasks.filter(({ task, role }) => {
            if (
                summaryFilter === "assigned" &&
                task.assignee_id !== currentUser.user_id
            ) {
                return false;
            }

            if (
                summaryFilter === "created" &&
                task.created_by !== currentUser.user_id
            ) {
                return false;
            }

            if (
                summaryFilter === "reviewing" &&
                task.reviewer_id !== currentUser.user_id
            ) {
                return false;
            }

            if (summaryFilter === "completed" && task.status !== "done") {
                return false;
            }

            if (filters.status !== "all" && task.status !== filters.status) {
                return false;
            }

            if (
                filters.priority !== "all" &&
                task.priority !== Number(filters.priority)
            ) {
                return false;
            }

            if (
                filters.projectId !== "all" &&
                task.project_id !== Number(filters.projectId)
            ) {
                return false;
            }

            if (filters.role !== "all" && role !== filters.role) {
                return false;
            }

            return true;
        });
    }, [tasks, filters, summaryFilter, currentUser]);

    /*
     * Pagination
     */
    const totalPages = Math.max(
        1,
        Math.ceil(filteredTasks.length / rowsPerPage),
    );

    const paginatedTasks = filteredTasks.slice(
        (page - 1) * rowsPerPage,
        page * rowsPerPage,
    );

    useEffect(() => {
        if (page > totalPages) {
            setPage(totalPages);
        }
    }, [page, totalPages]);

    /*
     * Summary card filtering
     */
    function changeSummaryFilter(filter: SummaryFilter) {
        setSummaryFilter(filter);
        setPage(1);
    }

    function clearFilters() {
        setFilters(initialFilters);
        setSummaryFilter("all");
        setPage(1);
    }

    /*
     * Open task details
     *
     * Members are fetched only when needed.
     */
    async function handleSelectTask(task: TaskResponse) {
        setError("");

        try {
            const members = await getProjectMembers(task.project_id);

            setSelectedTaskMembers(members);

            setSelectedTask(task);
        } catch (error) {
            setError(getApiErrorMessage(error));
        }
    }

    /*
     * Close task details with your animation
     */
    function closeTaskPanel() {
        if (isTaskPanelClosing) {
            return;
        }

        setIsTaskPanelClosing(true);

        setTimeout(() => {
            setSelectedTask(null);
            setSelectedTaskMembers([]);
            setIsTaskPanelClosing(false);
        }, 320);
    }

    /*
     * Real PATCH task integration
     */
    async function handleUpdateTask(data: TaskUpdate) {
        if (!selectedTask || !currentUser) {
            return;
        }

        /*
         * Intentionally no try/catch here.
         *
         * TaskDetailsPanel catches the rejected
         * request and sends the error to ErrorToast.
         */
        const updatedTask = await updateTask(
            selectedTask.project_id,
            selectedTask.task_id,
            data,
        );

        const stillBelongsToUser = taskBelongsToUser(
            updatedTask,
            currentUser.user_id,
        );

        /*
         * User may remove themselves as assignee /
         * reviewer and therefore the task might no
         * longer belong on My Tasks.
         */
        if (!stillBelongsToUser) {
            setTasks((current) =>
                current.filter(
                    ({ task }) => task.task_id !== updatedTask.task_id,
                ),
            );

            closeTaskPanel();
            return;
        }

        setTasks((current) =>
            current.map((entry) =>
                entry.task.task_id === updatedTask.task_id
                    ? {
                          ...entry,
                          task: updatedTask,
                          role: getTaskRole(updatedTask, currentUser.user_id),
                      }
                    : entry,
            ),
        );

        setSelectedTask(updatedTask);
    }

    /*
     * Resolve the owner of the project belonging
     * to the currently selected task.
     */
    const selectedProject = selectedTask
        ? projects.find(
              (project) => project.project_id === selectedTask.project_id,
          )
        : undefined;

    if (loading) {
        return (
            <div className="my-tasks-page">
                <Navbar />

                <ErrorToast message={error} onClose={() => setError("")} />

                <main className="my-tasks-content">
                    <p>Loading tasks...</p>
                </main>
            </div>
        );
    }

    return (
        <div className="my-tasks-page">
            <Navbar />

            <ErrorToast message={error} onClose={() => setError("")} />

            <main className="my-tasks-content">
                <section className="my-tasks-heading">
                    <h1>My Tasks</h1>

                    <p>All tasks across your projects.</p>
                </section>

                <section className="my-tasks-summary">
                    <button
                        type="button"
                        className={`summary-button summary-all ${
                            summaryFilter === "all" ? "active" : ""
                        }`}
                        onClick={() => changeSummaryFilter("all")}
                    >
                        <StatCard
                            value={tasks.length}
                            label="All"
                            icon={<ListTodo size={20} />}
                        />
                    </button>

                    <button
                        type="button"
                        className={`summary-button summary-assigned ${
                            summaryFilter === "assigned" ? "active" : ""
                        }`}
                        onClick={() => changeSummaryFilter("assigned")}
                    >
                        <StatCard
                            value={assignedCount}
                            label="Assigned to me"
                            icon={<UserRound size={20} />}
                        />
                    </button>

                    <button
                        type="button"
                        className={`summary-button summary-created ${
                            summaryFilter === "created" ? "active" : ""
                        }`}
                        onClick={() => changeSummaryFilter("created")}
                    >
                        <StatCard
                            value={createdCount}
                            label="Created by me"
                            icon={<PenLine size={20} />}
                        />
                    </button>

                    <button
                        type="button"
                        className={`summary-button summary-reviewing ${
                            summaryFilter === "reviewing" ? "active" : ""
                        }`}
                        onClick={() => changeSummaryFilter("reviewing")}
                    >
                        <StatCard
                            value={reviewingCount}
                            label="Reviewing"
                            icon={<Eye size={20} />}
                        />
                    </button>

                    <button
                        type="button"
                        className={`summary-button summary-completed ${
                            summaryFilter === "completed" ? "active" : ""
                        }`}
                        onClick={() => changeSummaryFilter("completed")}
                    >
                        <StatCard
                            value={completedCount}
                            label="Completed"
                            icon={<CircleCheckBig size={20} />}
                        />
                    </button>
                </section>

                <section className="my-tasks-panel">
                    <TaskFilters
                        filters={filters}
                        projects={projects}
                        onChange={(newFilters) => {
                            setFilters(newFilters);

                            setPage(1);
                        }}
                        onClear={clearFilters}
                    />

                    <div className="my-tasks-table">
                        <div className="my-tasks-table-header">
                            <span>Task</span>
                            <span>Project</span>
                            <span>Role</span>
                            <span>Priority</span>
                            <span>Status</span>
                            <span>Due date</span>
                        </div>

                        {paginatedTasks.length > 0 ? (
                            paginatedTasks.map(
                                ({ task, projectName, role }) => (
                                    <TaskTableRow
                                        key={task.task_id}
                                        name={task.task_name}
                                        description={task.task_description}
                                        projectName={projectName}
                                        role={role}
                                        priority={task.priority}
                                        status={task.status}
                                        dueDate={task.task_deadline}
                                        onClick={() => handleSelectTask(task)}
                                    />
                                ),
                            )
                        ) : (
                            <div className="my-tasks-empty">
                                No tasks match these filters.
                            </div>
                        )}
                    </div>

                    <footer className="my-tasks-pagination">
                        <span>
                            Showing{" "}
                            {filteredTasks.length === 0
                                ? 0
                                : (page - 1) * rowsPerPage + 1}{" "}
                            to{" "}
                            {Math.min(page * rowsPerPage, filteredTasks.length)}{" "}
                            of {filteredTasks.length} tasks
                        </span>

                        <div className="pagination-controls">
                            <button
                                type="button"
                                disabled={page === 1}
                                onClick={() =>
                                    setPage((current) =>
                                        Math.max(1, current - 1),
                                    )
                                }
                            >
                                ‹
                            </button>

                            {Array.from(
                                {
                                    length: totalPages,
                                },
                                (_, index) => index + 1,
                            ).map((pageNumber) => (
                                <button
                                    type="button"
                                    key={pageNumber}
                                    className={
                                        page === pageNumber ? "active" : ""
                                    }
                                    onClick={() => setPage(pageNumber)}
                                >
                                    {pageNumber}
                                </button>
                            ))}

                            <button
                                type="button"
                                disabled={page === totalPages}
                                onClick={() =>
                                    setPage((current) =>
                                        Math.min(totalPages, current + 1),
                                    )
                                }
                            >
                                ›
                            </button>
                        </div>
                    </footer>
                </section>
            </main>

            {selectedTask && selectedProject && currentUser && (
                <>
                    <div
                        className={`task-panel-backdrop ${
                            isTaskPanelClosing ? "closing" : ""
                        }`}
                        onClick={closeTaskPanel}
                    />

                    <TaskDetailsPanel
                        task={selectedTask}
                        members={selectedTaskMembers}
                        currentUserId={currentUser.user_id}
                        ownerId={selectedProject.owner_id}
                        isClosing={isTaskPanelClosing}
                        onClose={closeTaskPanel}
                        onUpdate={handleUpdateTask}
                        onError={setError}
                    />
                </>
            )}
        </div>
    );
}
