import { GreeksResponse } from "../Model/OptionData";

export interface IFutureDataProvider {
    fetchFutureSymbols(): Promise<string[]>;
}

class FutureDataProvider implements IFutureDataProvider {
    fetchFutureSymbols = async (): Promise<string[]> => {
        const response = await fetch('/api/futures');
        if (!response.ok) {
            throw new Error('Failed to fetch futures');
        }
        return response.json();
        // return ["IF2411", "IF2412", "IF2501", "HF2410", "HF2411", "HF2412"];
    };
}

export const futureDataProvider = new FutureDataProvider()