interface Trait {
  label: string;
  description: string;
}

interface Speaking {
  role: string;
  content: string;
  reply: string;
}

interface Distinctive {
  name: string;
  content: string;
}

export interface CharacterCard {
  id: number;
  avatar?: string;
  name?: string;
  description?: string;
  background_story?: string;

  traits?: Trait[];
  speakings?: Speaking[];
  distinct?: Distinctive[];
}