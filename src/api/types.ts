export type DemoAuthResponse = {
   userId: string;
  displayName?: string;
};

export type Role = "Frontend" | "Backend" | "Matching" | "Platform";
export type RolePref = "Frontend" | "Backend" | "Matching" | "Platform";


// types.ts

export type ContactInfo = {
  discord?: string;
  linkedin?: string;
};


export type ProfileUpsertRequest = {
  courseCode: string;
  userId: string;

  displayName?: string;
  roles: string[];
  skills: string[];
  availability: string[];
  goals?: string;
  contact?: { discord?: string; linkedin?: string };
};

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
  rolePrefs?: Role[];         // Backend sends rolePrefs
  roles?: Role[];              // Alias for compatibility
  skills: string[];
  availability: string[];
  lastActiveAt?: string;       // Backend sends lastActiveAt (ISO datetime)
  lastActive?: string;         // Formatted version (e.g. "active today")
  reasons?: string[];          // "Why this match"
};

export type RecommendationsResponse = {
  candidates: RecommendationUser[];
};

export type PodMember = {
  userId: string;
  displayName: string;
  rolePrefs?: Role[];          // Backend sends rolePrefs
  roles?: Role[];              // Alias for compatibility
  skills?: string[];
  availability?: string[];
  lastActiveAt?: string;       // Backend sends lastActiveAt (ISO datetime)
  lastActive?: string;         // Formatted version
  isMutual?: boolean;          // Computed from unlockedContactIds
  contactUnlocked?: boolean;   // Computed from unlockedContactIds
  contact?: {
    linkedin?: string;
    discord?: string;
    email?: string;
  };
};

export type PodState = {
  hasPod?: boolean;            // Backend sends hasPod: false when no pod
  podId?: string;
  courseCode?: string;
  leaderId?: string;           // Backend sends leaderId
  leaderUserId?: string;       // Alias for compatibility
  hubLink?: string;
  members: PodMember[];
  unlockedContactIds?: string[]; // Backend sends array of unlocked user IDs
  memberIds?: string[];        // Backend also sends memberIds
};

export type AskResponse = {
  layer: 1 | 2 | 3;
  answer: string;
  links?: string[] | { title: string; url: string }[]; // Backend sends string[], frontend expects objects
};

export type TicketResponse = {
  ticketId: string;
  createdAt?: string;
};
