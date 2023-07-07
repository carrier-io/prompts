const ApiFetchPrompts = async () => {
    const api_url = V.build_api_url('prompts', 'prompts')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}`, {
        method: 'GET',
    })
    return res.json();
}

const ApiFetchPromptById = async (promptId) => {
    const api_url = V.build_api_url('prompts', 'prompt')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}/${promptId}`, {
        method: 'GET',
    })
    return res.json();
}

const ApiCreatePrompt = async (promptName) => {
    const api_url = V.build_api_url('prompts', 'prompts')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "name": promptName,
            "type": "freeform",
            "prompt": "",
        })
    })
    return res.json();
}

const ApiUpdatePrompt = async (prompt) => {
    const api_url = V.build_api_url('prompts', 'prompt')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "id": prompt.id,
            "name": prompt.name,
            "type": "freeform",
            "prompt": prompt.prompt,
            // "model_settings": prompt.integration_settings,
        })
    })
    return res.json();
}

const ApiCreateExample = async (promptId, input, output) => {
    const api_url = V.build_api_url('prompts', 'example')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "prompt_id": promptId,
            "input": input,
            "output": output,
        })
    })
    return res.json();
}

const ApiRunTest = async (prompt, input, integrationId) => {
    const api_url = V.build_api_url('prompts', 'predict')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "prompt_id": prompt.id,
            "integration_id": integrationId,
            "integration_settings": prompt.integration_settings,
            "input": input,
        })
    })
    return res.json();
}

const ApiDeletePrompt = async (promptId) => {
    const api_url = V.build_api_url('prompts', 'prompt')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}/${promptId}`, {
        method: 'DELETE',
    })
}

const ApiDeleteExample = async (exampleId) => {
    const api_url = V.build_api_url('prompts', 'example')
    const res = await fetch(`${api_url}/${getSelectedProjectId()}/${exampleId}`, {
        method: 'DELETE',
    })
}
