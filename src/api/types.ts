export type DemoAuthResponse = {
   userId: string;
  displayName?: string;
};

export type Role = "Frontend" | "Backend" | "Matching" | "Platform";
export type RolePref = "Frontend" | "Backend" | "Matching" | "Platform";



export type Profile = {
  userId: string;
  courseCode: string;
  displayName?: string;
  roles: Role[];
  skills: string[];
  availability: string[];
  goals?: string[];
};

export type RecommendationUser = {
  userId: string;
  displayName: string;
  roles: Role[];
  skills: string[];
  availability: string[];
  lastActive?: string;        // e.g. "active today"
  reasons?: string[];         // "Why this match"
};

export type RecommendationsResponse = {
  candidates: RecommendationUser[];
};

export type PodMember = {
  userId: string;
  displayName: string;
  roles?: Role[];
  skills?: string[];
  lastActive?: string;
  isMutual?: boolean;         // unlocked contact if true (or your backend field)
  contact?: {
    linkedin?: string;
    discord?: string;
    email?: string;
  };
};

export type PodState = {
  podId?: string;
  courseCode: string;
  leaderUserId?: string;
  hubLink?: string;
  members: PodMember[];
};

export type AskResponse = {
  layer: 1 | 2 | 3;
  answer: string;
  links?: { title: string; url: string }[];
};

export type TicketResponse = {
  ticketId: string;
  createdAt?: string;
};
