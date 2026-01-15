export type IdentifyResult = {
    best_match: { id: string; name: string; score: number } | null;
    candidates: { id: string; name: string; score: number }[];
    extracted_text: string;
  };
  
  export type Msg =
    | { id: string; role: "user"; type: "text"; text: string }
    | { id: string; role: "user"; type: "image"; uri: string; text?: string }
    | { id: string; role: "assistant"; type: "text"; text: string }
    | { id: string; role: "assistant"; type: "identify"; payload: IdentifyResult }
    | { id: string; role: "assistant"; type: "typing" }
    | { id: string; role: "assistant"; type: "pill_result"; payload: { id: string; name: string } };
  