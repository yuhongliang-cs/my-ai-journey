from openai import OpenAI
import getpass

# 可选角色与对应的 system prompt
ROLES = {
    "1": {"name": "编程老师", "prompt": "你是一位耐心的编程老师，擅长用通俗易懂的方式讲解编程概念，并给出代码示例。"},
    "2": {"name": "面试官", "prompt": "你是一位严谨的面试官，擅长提出有深度的问题，考察应聘者的思维能力和技术功底。"},
    "3": {"name": "翻译", "prompt": "你是一位专业的翻译助手，能够准确、自然地进行中英互译，并解释关键用词。"},
}


def choose_role():
    """让用户选择角色，返回对应的 system prompt 内容。"""
    print("\n请选择 AI 角色：")
    for key, role in ROLES.items():
        print(f"  {key}. {role['name']}")
    while True:
        choice = input("请输入角色编号（默认 1）: ").strip()
        if not choice:
            choice = "1"
        if choice in ROLES:
            print(f"已选择角色：{ROLES[choice]['name']}\n")
            return ROLES[choice]["prompt"]
        print("无效输入，请重新选择。")


def create_client():
    """提示用户输入 API Key 并初始化 OpenAI 客户端。"""
    api_key = getpass.getpass("请输入你的 API Key（输入内容不会显示）: ").strip()
    if not api_key:
        raise ValueError("API Key 不能为空，请重新运行程序并输入有效的 Key。")
    return OpenAI(
        api_key=api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )


def main():
    client = create_client()
    system_prompt = choose_role()
    messages = [{"role": "system", "content": system_prompt}]

    print("开始对话吧！输入 '清空' 可重置对话，'切换角色' 可更换角色，'退出' 结束程序。\n")

    while True:
        user_input = input("你: ").strip()
        if not user_input:
            continue

        if user_input == "退出":
            print("再见！")
            break

        if user_input == "清空":
            messages = [{"role": "system", "content": system_prompt}]
            print("对话已清空，可以开始新的话题。\n")
            continue

        if user_input == "切换角色":
            system_prompt = choose_role()
            messages = [{"role": "system", "content": system_prompt}]
            print("角色已切换，对话已清空。\n")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            stream = client.chat.completions.create(
                model="glm-4.5-flash",
                messages=messages,
                stream=True
            )

            print("AI: ", end="", flush=True)
            reply = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    print(delta, end="", flush=True)
                    reply += delta
            print()

            messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f"\n[错误] 请求失败：{e}")
            # 移除失败的 user 消息，避免污染对话历史
            messages.pop()


if __name__ == "__main__":
    main()
