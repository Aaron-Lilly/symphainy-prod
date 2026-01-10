export interface CardData {
  id: string;
  text: string;
  x: number;
  y: number;
}

export interface Connection {
  source: string;
  destination: string;
}

export interface ConnectionData {
  cards: CardData[];
  connections: Connection[];
}
