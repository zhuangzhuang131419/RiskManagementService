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
        // return ["IO2410", "IO2411", "IO2412", "HO2410", "HO2411", "HO2412"];
    };
}

export const futureDataProvider = new FutureDataProvider()