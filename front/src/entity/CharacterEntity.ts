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

  trait?: Trait[];
  speak?: Speaking[];
  distinctive?: Distinctive[];
}

export interface CreateCharacterDto {
  avatar?: string;
  name?: string;
  description?: string;
  background_story?: string;

  trait?: Trait[];
  speak?: Speaking[];
  distinctive?: Distinctive[];
}