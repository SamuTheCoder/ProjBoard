import { useEffect, useState } from "react";

import { useNavigate, useParams } from "react-router-dom";

import { Navbar } from "../components/Navbar";
import { Button } from "../components/Button";

import {
    ProjectSidebar,
    type ProjectSection,
} from "../components/ProjectSidebar/ProjectSidebar";

import { StatCard } from "../components/StatCard/StatCard";
import { TaskColumn } from "../components/TaskColumn/TaskColumn";
import { TaskCard } from "../components/TaskCard/TaskCard";

import { TaskDetailsPanel } from "../components/TaskDetailsPanel/TaskDetailsPanel";

import { CreateTaskModal } from "../components/CreateTaskModal/CreateTaskModal";

import { createTask, getProjectTasks, updateTask } from "../api/task";

import { deleteProject, getProject } from "../api/project";

import {
    addProjectMember,
    getProjectMembers,
    removeProjectMember,
    transferProjectOwnership,
} from "../api/member";

import { getCurrentUser } from "../api/user";

import { getApiErrorMessage } from "../api/errors";

import type { TaskCreate, TaskResponse, TaskUpdate } from "../types/task";

import type { ProjectResponse } from "../types/project";

import type { ProjectMemberResponse } from "../types/member";

import type { UserResponse } from "../types/auth";

import "./ProjectDashboard.css";

import {
    ListTodo,
    Archive,
    CircleDot,
    LoaderCircle,
    Eye,
    CircleCheckBig,
} from "lucide-react";

import { ErrorToast } from "../components/ErrorToast/ErrorToast";

export function ProjectDashboard() {
    const { projectId } = useParams();

    const navigate = useNavigate();

    const numericProjectId = Number(projectId);

    const [activeSection, setActiveSection] =
        useState<ProjectSection>("dashboard");

    const [isCreateTaskOpen, setIsCreateTaskOpen] = useState(false);

    const [selectedTask, setSelectedTask] = useState<TaskResponse | null>(null);

    const [project, setProject] = useState<ProjectResponse | null>(null);

    const [tasks, setTasks] = useState<TaskResponse[]>([]);

    const [members, setMembers] = useState<ProjectMemberResponse[]>([]);

    const [currentUser, setCurrentUser] = useState<UserResponse | null>(null);

    const [pageError, setPageError] = useState("");

    const [taskSearch, setTaskSearch] = useState("");

    const [statusFilter, setStatusFilter] = useState("all");

    const [priorityFilter, setPriorityFilter] = useState("all");

    const [assigneeFilter, setAssigneeFilter] = useState("all");

    const [memberSearch, setMemberSearch] = useState("");

    const [newOwnerId, setNewOwnerId] = useState("");

    const [newMemberUsername, setNewMemberUsername] = useState("");

    useEffect(() => {
        async function loadDashboard() {
            if (!projectId || Number.isNaN(numericProjectId)) {
                return;
            }

            setPageError("");

            try {
                const [projectData, tasksData, membersData, userData] =
                    await Promise.all([
                        getProject(numericProjectId),

                        getProjectTasks(numericProjectId),

                        getProjectMembers(numericProjectId),

                        getCurrentUser(),
                    ]);

                setProject(projectData);
                setTasks(tasksData);
                setMembers(membersData);
                setCurrentUser(userData);
            } catch (error) {
                setPageError(getApiErrorMessage(error));
            }
        }

        loadDashboard();
    }, [projectId]);

    const backlog = tasks.filter((task) => task.status === "backlog");

    const ready = tasks.filter((task) => task.status === "ready");

    const inProgress = tasks.filter((task) => task.status === "in_progress");

    const toReview = tasks.filter((task) => task.status === "to_review");

    const done = tasks.filter((task) => task.status === "done");

    const [isTaskPanelClosing, setIsTaskPanelClosing] = useState(false);

    function closeTaskPanel() {
        if (isTaskPanelClosing) return;

        setIsTaskPanelClosing(true);

        setTimeout(() => {
            setSelectedTask(null);
            setIsTaskPanelClosing(false);
        }, 320);
    }

    const isOwner =
        project !== null &&
        currentUser !== null &&
        project.owner_id === currentUser.user_id;

    function getMember(userId: number | null) {
        if (!userId) return undefined;

        return members.find((member) => member.user_id === userId);
    }

    function getInitials(userId: number | null) {
        const member = getMember(userId);

        if (!member) return undefined;

        const initials = `${member.first_name[0] ?? ""}${member.last_name[0] ?? ""}`;

        return (
            initials.toUpperCase() || member.username.slice(0, 2).toUpperCase()
        );
    }

    async function handleCreateTask(data: TaskCreate) {
        const newTask = await createTask(numericProjectId, data);

        setTasks((current) => [...current, newTask]);

        setIsCreateTaskOpen(false);
    }

    async function handleUpdateTask(taskId: number, data: TaskUpdate) {
        const updatedTask = await updateTask(numericProjectId, taskId, data);

        setTasks((current) =>
            current.map((task) =>
                task.task_id === updatedTask.task_id ? updatedTask : task,
            ),
        );

        setSelectedTask(updatedTask);
    }

    async function handleRemoveMember(userId: number) {
        const confirmed = window.confirm(
            "Remove this member from the project?",
        );

        if (!confirmed) return;

        setPageError("");

        try {
            await removeProjectMember(numericProjectId, userId);

            const [updatedProject, updatedMembers, updatedTasks] =
                await Promise.all([
                    getProject(numericProjectId),

                    getProjectMembers(numericProjectId),

                    getProjectTasks(numericProjectId),
                ]);

            setProject(updatedProject);
            setMembers(updatedMembers);
            setTasks(updatedTasks);

            setSelectedTask(null);
        } catch (error) {
            setPageError(getApiErrorMessage(error));
        }
    }

    async function handleTransferOwnership() {
        if (!newOwnerId) return;

        const confirmed = window.confirm(
            "Transfer project ownership to this member?",
        );

        if (!confirmed) return;

        setPageError("");

        try {
            await transferProjectOwnership(
                numericProjectId,
                Number(newOwnerId),
            );

            const [updatedProject, updatedMembers] = await Promise.all([
                getProject(numericProjectId),

                getProjectMembers(numericProjectId),
            ]);

            setProject(updatedProject);
            setMembers(updatedMembers);

            setNewOwnerId("");
        } catch (error) {
            setPageError(getApiErrorMessage(error));
        }
    }

    async function handleDeleteProject() {
        const confirmed = window.confirm(
            `Delete "${project?.project_name}" permanently?`,
        );

        if (!confirmed) return;

        setPageError("");

        try {
            await deleteProject(numericProjectId);

            navigate("/projects");
        } catch (error) {
            setPageError(getApiErrorMessage(error));
        }
    }

    async function handleAddMember() {
        const username = newMemberUsername.trim();

        if (!username) return;

        setPageError("");

        try {
            await addProjectMember(numericProjectId, { username });

            const [updatedMembers, updatedProject] = await Promise.all([
                getProjectMembers(numericProjectId),
                getProject(numericProjectId),
            ]);

            setMembers(updatedMembers);
            setProject(updatedProject);

            setNewMemberUsername("");
        } catch (error) {
            setPageError(getApiErrorMessage(error));
        }
    }

    const filteredTasks = tasks.filter((task) => {
        const search = taskSearch.trim().toLowerCase();

        if (
            search &&
            !task.task_name.toLowerCase().includes(search) &&
            !(task.task_description ?? "").toLowerCase().includes(search)
        ) {
            return false;
        }

        if (statusFilter !== "all" && task.status !== statusFilter) {
            return false;
        }

        if (
            priorityFilter !== "all" &&
            task.priority !== Number(priorityFilter)
        ) {
            return false;
        }

        if (assigneeFilter === "unassigned" && task.assignee_id !== null) {
            return false;
        }

        if (
            assigneeFilter !== "all" &&
            assigneeFilter !== "unassigned" &&
            task.assignee_id !== Number(assigneeFilter)
        ) {
            return false;
        }

        return true;
    });

    const filteredMembers = members.filter((member) => {
        const search = memberSearch.trim().toLowerCase();

        if (!search) return true;

        return (
            member.username.toLowerCase().includes(search) ||
            member.email.toLowerCase().includes(search) ||
            member.first_name.toLowerCase().includes(search) ||
            member.last_name.toLowerCase().includes(search)
        );
    });

    if (!project) {
        return (
            <div className="project-dashboard">
                <Navbar />
                <ErrorToast
                    message={pageError}
                    onClose={() => setPageError("")}
                />

                <div className="project-loading">Loading project...</div>
            </div>
        );
    }

    return (
        <div className="project-dashboard">
            <Navbar />
            <ErrorToast message={pageError} onClose={() => setPageError("")} />

            <div className="project-dashboard-layout">
                <ProjectSidebar
                    activeSection={activeSection}
                    onSectionChange={(section) => {
                        setActiveSection(section);

                        setSelectedTask(null);
                    }}
                />

                <main className="project-main">
                    <section className="project-header">
                        <div>
                            <h1>{project.project_name}</h1>

                            <p>
                                {project.project_description ||
                                    "No project description."}
                            </p>
                        </div>

                        {(activeSection === "dashboard" ||
                            activeSection === "tasks") && (
                            <div className="project-header-actions">
                                <Button
                                    type="button"
                                    onClick={() => setIsCreateTaskOpen(true)}
                                >
                                    + New Task
                                </Button>
                            </div>
                        )}
                    </section>

                    {activeSection === "dashboard" && (
                        <>
                            <section className="project-stats">
                                <StatCard
                                    value={tasks.length}
                                    label="Total Tasks"
                                    icon={<ListTodo size={20} />}
                                />

                                <StatCard
                                    value={backlog.length}
                                    label="Backlog"
                                    icon={<Archive size={20} />}
                                />

                                <StatCard
                                    value={ready.length}
                                    label="Ready"
                                    icon={<CircleDot size={20} />}
                                />

                                <StatCard
                                    value={inProgress.length}
                                    label="In Progress"
                                    icon={<LoaderCircle size={20} />}
                                />

                                <StatCard
                                    value={toReview.length}
                                    label="To Review"
                                    icon={<Eye size={20} />}
                                />

                                <StatCard
                                    value={done.length}
                                    label="Done"
                                    icon={<CircleCheckBig size={20} />}
                                />
                            </section>

                            <section className="task-board">
                                <TaskColumn
                                    title="Backlog"
                                    count={backlog.length}
                                >
                                    {backlog.map((task) => (
                                        <TaskCard
                                            key={task.task_id}
                                            name={task.task_name}
                                            priority={task.priority}
                                            assigneeInitials={getInitials(
                                                task.assignee_id,
                                            )}
                                            onClick={() =>
                                                setSelectedTask(task)
                                            }
                                        />
                                    ))}
                                </TaskColumn>

                                <TaskColumn title="Ready" count={ready.length}>
                                    {ready.map((task) => (
                                        <TaskCard
                                            key={task.task_id}
                                            name={task.task_name}
                                            priority={task.priority}
                                            assigneeInitials={getInitials(
                                                task.assignee_id,
                                            )}
                                            onClick={() =>
                                                setSelectedTask(task)
                                            }
                                        />
                                    ))}
                                </TaskColumn>

                                <TaskColumn
                                    title="In Progress"
                                    count={inProgress.length}
                                >
                                    {inProgress.map((task) => (
                                        <TaskCard
                                            key={task.task_id}
                                            name={task.task_name}
                                            priority={task.priority}
                                            assigneeInitials={getInitials(
                                                task.assignee_id,
                                            )}
                                            onClick={() =>
                                                setSelectedTask(task)
                                            }
                                        />
                                    ))}
                                </TaskColumn>

                                <TaskColumn
                                    title="To Review"
                                    count={toReview.length}
                                >
                                    {toReview.map((task) => (
                                        <TaskCard
                                            key={task.task_id}
                                            name={task.task_name}
                                            priority={task.priority}
                                            assigneeInitials={getInitials(
                                                task.assignee_id,
                                            )}
                                            onClick={() =>
                                                setSelectedTask(task)
                                            }
                                        />
                                    ))}
                                </TaskColumn>

                                <TaskColumn title="Done" count={done.length}>
                                    {done.map((task) => (
                                        <TaskCard
                                            key={task.task_id}
                                            name={task.task_name}
                                            priority={task.priority}
                                            assigneeInitials={getInitials(
                                                task.assignee_id,
                                            )}
                                            onClick={() =>
                                                setSelectedTask(task)
                                            }
                                        />
                                    ))}
                                </TaskColumn>
                            </section>
                        </>
                    )}

                    {activeSection === "tasks" && (
                        <section className="dashboard-section">
                            <div className="section-heading">
                                <h2>Tasks</h2>

                                <span>{filteredTasks.length} tasks</span>
                            </div>

                            <div className="task-filters">
                                <input
                                    placeholder="Search tasks..."
                                    value={taskSearch}
                                    onChange={(event) =>
                                        setTaskSearch(event.target.value)
                                    }
                                />

                                <select
                                    value={statusFilter}
                                    onChange={(event) =>
                                        setStatusFilter(event.target.value)
                                    }
                                >
                                    <option value="all">All statuses</option>

                                    <option value="backlog">Backlog</option>

                                    <option value="ready">Ready</option>

                                    <option value="in_progress">
                                        In Progress
                                    </option>

                                    <option value="to_review">To Review</option>

                                    <option value="done">Done</option>
                                </select>

                                <select
                                    value={priorityFilter}
                                    onChange={(event) =>
                                        setPriorityFilter(event.target.value)
                                    }
                                >
                                    <option value="all">All priorities</option>

                                    {[1, 2, 3, 4, 5].map((priority) => (
                                        <option key={priority} value={priority}>
                                            Priority {priority}
                                        </option>
                                    ))}
                                </select>

                                <select
                                    value={assigneeFilter}
                                    onChange={(event) =>
                                        setAssigneeFilter(event.target.value)
                                    }
                                >
                                    <option value="all">All assignees</option>

                                    <option value="unassigned">
                                        Unassigned
                                    </option>

                                    {members.map((member) => (
                                        <option
                                            key={member.user_id}
                                            value={member.user_id}
                                        >
                                            {member.first_name}{" "}
                                            {member.last_name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="task-list">
                                {filteredTasks.map((task) => {
                                    const assignee = getMember(
                                        task.assignee_id,
                                    );

                                    return (
                                        <button
                                            key={task.task_id}
                                            className="task-list-row"
                                            onClick={() =>
                                                setSelectedTask(task)
                                            }
                                        >
                                            <div>
                                                <strong>
                                                    {task.task_name}
                                                </strong>
                                            </div>

                                            <span>{task.status}</span>

                                            <span>
                                                Priority {task.priority}
                                            </span>

                                            <span>
                                                {assignee
                                                    ? `${assignee.first_name} ${assignee.last_name}`
                                                    : "Unassigned"}
                                            </span>
                                        </button>
                                    );
                                })}
                            </div>
                        </section>
                    )}

                    {activeSection === "members" && (
                        <section className="dashboard-section">
                            <div className="section-heading">
                                <h2>Members</h2>

                                <span>{members.length} members</span>
                            </div>

                            {isOwner && (
                                <div className="add-member-form">
                                    <input
                                        type="text"
                                        placeholder="Enter username"
                                        value={newMemberUsername}
                                        onChange={(event) =>
                                            setNewMemberUsername(
                                                event.target.value,
                                            )
                                        }
                                    />

                                    <button
                                        type="button"
                                        disabled={!newMemberUsername.trim()}
                                        onClick={handleAddMember}
                                    >
                                        + Add Member
                                    </button>
                                </div>
                            )}

                            <input
                                className="member-search"
                                placeholder="Search members..."
                                value={memberSearch}
                                onChange={(event) =>
                                    setMemberSearch(event.target.value)
                                }
                            />

                            <div className="member-list">
                                {filteredMembers.map((member) => (
                                    <div
                                        key={member.user_id}
                                        className="member-row"
                                    >
                                        <div className="member-avatar">
                                            {getInitials(member.user_id)}
                                        </div>

                                        <div className="member-info">
                                            <strong>
                                                {member.first_name}{" "}
                                                {member.last_name}
                                            </strong>

                                            <span>
                                                @{member.username} ·{" "}
                                                {member.email}
                                            </span>
                                        </div>

                                        <span className="member-role">
                                            {member.role}
                                        </span>

                                        {isOwner &&
                                            member.user_id !==
                                                project.owner_id && (
                                                <button
                                                    className="remove-member-button"
                                                    onClick={() =>
                                                        handleRemoveMember(
                                                            member.user_id,
                                                        )
                                                    }
                                                >
                                                    Remove
                                                </button>
                                            )}
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {activeSection === "settings" && (
                        <section className="dashboard-section settings-section">
                            <div className="section-heading">
                                <h2>Project Settings</h2>
                            </div>

                            {!isOwner ? (
                                <div className="settings-card">
                                    Only the project owner can change project
                                    administration settings.
                                </div>
                            ) : (
                                <>
                                    <div className="settings-card">
                                        <h3>Transfer ownership</h3>

                                        <p>
                                            Transfer ownership to another member
                                            of this project.
                                        </p>

                                        <div className="settings-action">
                                            <select
                                                value={newOwnerId}
                                                onChange={(event) =>
                                                    setNewOwnerId(
                                                        event.target.value,
                                                    )
                                                }
                                            >
                                                <option value="">
                                                    Select new owner
                                                </option>

                                                {members
                                                    .filter(
                                                        (member) =>
                                                            member.user_id !==
                                                            project.owner_id,
                                                    )
                                                    .map((member) => (
                                                        <option
                                                            key={member.user_id}
                                                            value={
                                                                member.user_id
                                                            }
                                                        >
                                                            {member.first_name}{" "}
                                                            {member.last_name}
                                                        </option>
                                                    ))}
                                            </select>

                                            <button
                                                disabled={!newOwnerId}
                                                onClick={
                                                    handleTransferOwnership
                                                }
                                            >
                                                Transfer
                                            </button>
                                        </div>
                                    </div>

                                    <div className="settings-card danger-zone">
                                        <h3>Delete project</h3>

                                        <p>
                                            Permanently delete this project and
                                            its data.
                                        </p>

                                        <button onClick={handleDeleteProject}>
                                            Delete Project
                                        </button>
                                    </div>
                                </>
                            )}
                        </section>
                    )}
                </main>
            </div>

            {selectedTask && currentUser && (
                <>
                    <div
                        className={`task-panel-backdrop ${
                            isTaskPanelClosing ? "closing" : ""
                        }`}
                        onClick={closeTaskPanel}
                    />

                    <TaskDetailsPanel
                        task={selectedTask}
                        members={members}
                        currentUserId={currentUser.user_id}
                        ownerId={project.owner_id}
                        isClosing={isTaskPanelClosing}
                        onClose={closeTaskPanel}
                        onError={setPageError}
                        onUpdate={(data) =>
                            handleUpdateTask(selectedTask.task_id, data)
                        }
                    />
                </>
            )}

            <CreateTaskModal
                isOpen={isCreateTaskOpen}
                members={members}
                onClose={() => setIsCreateTaskOpen(false)}
                onSubmit={handleCreateTask}
            />
        </div>
    );
}
