import { User } from "../Model/User";
import { GreeksResponse } from "../Model/OptionData";

export interface IUserDataProvider {
    fetchUsers(): Promise<User[]>;
    setUser(name: string): Promise<void>;
    fetchBaseline(): Promise<string>;
    setBaseline(baseline: string): Promise<void>;
}

class UserDataProvider implements IUserDataProvider {
    fetchUsers = async (): Promise<User[]> => {
        const response = await fetch('/api/users');
        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }
        return response.json();
        // return ["IF2411", "IF2412", "IF2501", "HF2410", "HF2411", "HF2412"];
    };

    setUser = async (name: string): Promise<void> => {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'user_name': name }),
        })
        if (!response.ok) {
            throw new Error('Failed to set user');
        }
        return response.json();
    }

    fetchBaseline = async (): Promise<string> => {
        const response = await fetch('/api/baseline', {
            method: 'GET'
        });
        if (!response.ok) {
            throw new Error('Failed to fetch baseline');
        }

        const data = await response.json(); // 使用 await 获取解析后的 JSON 数据
        console.log('fetchBaseline', data);
        return data.current_baseline; // 假设后端返回的数据结构包含 { current_baseline: ... }
    }

    setBaseline = async (baseline: string): Promise<void> => {
        const response = await fetch('/api/baseline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'baseline': baseline }),
        })
        if (!response.ok) {
            throw new Error('Failed to post baseline');
        }
        return response.json();
    }
}

export const userDataProvider = new UserDataProvider()