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
const valueFormatters = {
    // token: (value, row, index, field) => {
    //    return `<div class="d-flex text-wrap" style="max-width: 500px">${value}</div>`
    // }
}
const actionFormatters = {
    integrations: (value, row, index, field) => {

        const processIntegrations = integrations => {
            return integrations.map(({id, config}) => {
                return `
                    <option
                        value="${id}"
                        ${id === row.value && 'selected'}
                    >
                        ${config.name} | id: ${id}
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


var valueCellStyle = (value, row, index, field) => {
    return {
        css: {
            "max-width": "500px",
            // "overflow": "hidden",
            "text-wrap": "wrap",
            // "white-space": "nowrap"
        }
    }
}

const artifact_download_url = V.build_api_url('prompts', 'config_download', {trailing_slash: true})

var downloadArtifactFormatter = (value, row, index) => {
    return `
        <a 
            href="${artifact_download_url}/${row['name']}" 
            class="fa fa-download btn-action" 
            download="${row['name']}"
        ></a>
    `
}
