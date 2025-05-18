interface Trait {
  label: string;
  description: string;
}

interface Personality {
  traits?: Trait[];
}

interface Background {
  background_story?: string;
}

interface Speaking {
  role: string;
  content: string;
  reply: string;
}

interface Behaviors {
  speakingStyle: Speaking[];
}

interface Distinctive {
  fieldName: string;
  fieldValue: string;
}

interface CustomizeFields {
  fields: Distinctive[];
}

export interface CharacterCard {
  id: number;
  avatar?: string;
  name?: string;
  description?: string;
  personality?: Personality;
  background?: Background;
  behaviors?: Behaviors;
  customize?: CustomizeFields;
}