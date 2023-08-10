const regenerateToken = async (index) => {
    const api_url = V.build_api_url('prompts', 'config', {trailing_slash: true})
    const resp = await fetch(api_url + V.project_id, {
        method: 'PUT',
    })
    if (resp.ok) {
        const {token} = await resp.json()
        V.registered_components.table_config.table_action('updateRow', {
            index: index,
            row: {value: token}
        })
        showNotify('SUCCESS', 'Token refreshed')
    } else {
        showNotify('ERROR', 'Token refresh error')
    }
}

const valueFormatters = {}

const actionFormatters = {
    integrations: (value, row, index, field) => {
        const processIntegrations = integrations => {
            return integrations.map(({id, config}) => {
                return `
                    <option
                        value="${id}"
                        ${id === row.value && 'selected'}
                    >
                        ${config.name}
                    </option>
                `
            })
        }
        const processGroup = (name, integrations) => {
            return `
                <optgroup label="${name}"></optgroup>
                ${processIntegrations(integrations)}
            `
        }

        return `
            <select class="custom-select"
                onchange="V.registered_components.table_config.table_action('updateRow', {
                    index: ${index},
                    row: {
                        value: parseInt(this.value)
                    }
                })"
            >
                ${Object.entries(value).map(
            ([group, integrations]) => processGroup(group, integrations)
        )}
            </select>
        `
    },
    token: (value, row, index, field) => {
        return `
            <button class="btn btn-secondary" onclick="regenerateToken(${index})">Regenerate token</button>
        `
    }
}

var valueFormatter = (value, row, index, field) => {
    const formatterFunc = valueFormatters[row.key]
    return formatterFunc === undefined ? value : formatterFunc(value, row, index, field)
}

var actionFormatter = (value, row, index, field) => {
    const formatterFunc = actionFormatters[row.key]
    return formatterFunc === undefined ? value : formatterFunc(value, row, index, field)
}

var tokenCellStyle = (value, row, index, field) => {
    return {
        css: {
            "max-width": "500px",
            "text-wrap": "wrap",
        }
    }
}


var downloadArtifactFormatter = (value, row, index) => {
    const artifact_download_url = V.build_api_url(
        'prompts',
        'config_bucket',
        {trailing_slash: true}
    )
    const file_name = encodeURIComponent(row['name'])
    return `
        <a 
            href="${artifact_download_url}${V.project_id}/${file_name}" 
            class="fa fa-download btn-action" 
            download="${row['name']}"
        ></a>
    `
}

const copyConfigToClip = () => {
    const textArea = document.createElement('textarea')
    const data = V.registered_components.table_config.table_action('getData').reduce((accum, item) => {
        accum[item.key] = item.value
        return accum
    }, {})
    textArea.value = JSON.stringify(data, null, 2)

    // Avoid scrolling to bottom
    textArea.style.top = '0'
    textArea.style.left = '0'
    textArea.style.position = 'fixed'

    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()

    try {
        const copySuccess = document.execCommand('copy')
        copySuccess ?
            showNotify('SUCCESS', 'Config copied to clipboard')
            :
            showNotify('ERROR', 'Error copying to clipboard')
    } catch (err) {
        showNotify('ERROR', 'Error copying to clipboard')
    }

    document.body.removeChild(textArea)
}