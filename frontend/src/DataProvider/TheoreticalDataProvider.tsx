import { GroupWingModelData } from "../Model/OptionData";

export interface ITheoreticalDataProvider {
    fetchWingModelData(): Promise<GroupWingModelData[]>;
    fetchIVData(symbol: string): Promise<Record<string, [number, number, number]>>;
}
class TheoreticalDataProvider implements ITheoreticalDataProvider {
    fetchWingModelData = async (): Promise<GroupWingModelData[]> => {
        const response = await fetch("/api/option/wing_model_para");
        if (!response.ok) {
            throw new Error("Failed to fetch wing model data");
        }
        return response.json();
    }

    fetchIVData = async (symbol: string): Promise<Record<string, [number, number, number]>> => {
        const response = await fetch(`/api/option/month_t_iv/${symbol}`);
        if (!response.ok) {
            throw new Error("Failed to fetch wing model data");
        }
        return response.json();
    }
}

export const theoreticalDataProvider = new TheoreticalDataProvider()