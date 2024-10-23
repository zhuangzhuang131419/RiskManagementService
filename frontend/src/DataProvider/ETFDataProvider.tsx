import { GreeksResponse } from "../Model/OptionData";

export interface IETFDataProvider {
    fetchFutureSymbols(): Promise<string[]>;
}

class ETFDataProvider implements IETFDataProvider {
    fetchFutureSymbols = async (): Promise<string[]> => {
        // const response = await fetch('/api/futures');
        // if (!response.ok) {
        //     throw new Error('Failed to fetch futures');
        // }
        // return response.json();
        return ["510300_2411", "510300_2412", "510300_2501", "510300_2502", "510300_2503", "510300_2504"];
    };
}

export const etfDataProvider = new ETFDataProvider()