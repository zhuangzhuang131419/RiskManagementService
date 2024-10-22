import { GreeksResponse } from "../Model/OptionData";

export interface IOptionDataProvider {
    fetchOptionSymbols(): Promise<string[]>;
    fetchOptionGreeks(symbol: string): Promise<GreeksResponse>;
}

class OptionDataProvider implements IOptionDataProvider {
    fetchOptionSymbols = async () => {
        const response = await fetch('/api/options');
        if (!response.ok) {
            throw new Error('Failed to fetch options');
        }
        return response.json();
    };

    fetchOptionGreeks = async (symbol: string): Promise<GreeksResponse> => {
        const response = await fetch(`/api/option/greeks?symbol=${symbol}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        console.log('symbol' + symbol)
        // 打印响应状态
        console.log('Response status: ' + response.status);
        console.log('Response status text: ' + response.statusText);
    
        // 解析并打印 JSON 数据
        const data = await response.json();
        console.log('Response data: ', data);
        
        return data;
    };
}

export const optionDataProvider = new OptionDataProvider()