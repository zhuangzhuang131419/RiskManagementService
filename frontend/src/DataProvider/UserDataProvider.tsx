import { Account } from "../Model/Account";
import { GreeksResponse } from "../Model/OptionData";

export interface IUserDataProvider {
    fetchUsers(): Promise<Account[]>;
}

class UserDataProvider implements IUserDataProvider {
    fetchUsers = async (): Promise<Account[]> => {
        const response = await fetch('/api/users');
        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }
        return response.json();
        // return ["IF2411", "IF2412", "IF2501", "HF2410", "HF2411", "HF2412"];
    };
}

export const userDataProvider = new UserDataProvider()