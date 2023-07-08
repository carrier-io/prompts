var ParamsTable = {
    parametersDeleteFormatter(value, row, index) {
        return `
            <button type="button" class="btn btn-default btn-xs btn-table btn-icon__xs" 
                onclick="ParamsTable.deleteParams(${index}, this, '${row.id}')">
                <i class="icon__18x18 icon-delete"></i>
            </button>
        `
    },
    inputFormatter(value, row, index, field) {
        return `
            <input type="text" class="form-control form-control-alternative"
                onchange="ParamsTable.updateCell(this, ${index}, '${field}', '${row.id}')" value="${value}">
            <div class="invalid-tooltip invalid-tooltip-custom"></div>
        `
    },
    deleteParams: (index, source, exampleId) => {
        const $table = $(source).closest('.params-table').bootstrapTable('remove', {
            field: '$index',
            values: [index]
        })
        $table.bootstrapTable('getData').length === 0 && $table.addClass('empty_data');
        if (exampleId.length < 10) vueVm.registered_components['prompts-params'].deleteExample(exampleId);
    },
    updateCell: (el, row, field, id) => {
        $(el.closest('table')).bootstrapTable(
            'updateCell',
            {index: row, field: field, value: el.value}
        )
        vueVm.registered_components['prompts-params'].checkFields(id);
    },
}