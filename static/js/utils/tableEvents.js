var ParamsTable = {
    parametersDeleteFormatter(value, row, index) {
        return `
            <button type="button" class="btn btn-default btn-xs btn-table btn-icon__xs" 
                onclick="ParamsTable.deleteParams(${index}, this, '${row.id}')">
                <i class="icon__18x18 icon-delete"></i>
            </button>
        `
    },
    textareaFormatter(value, row, index, field) {
        return `
            <div class="pb-1 position-relative">
                <textarea class="form-control form-control-alternative"
                    rows="3"
                    onchange="ParamsTable.updateCell(this, ${index}, '${field}', '${row.id}')" 
                    value="${value}">${value}</textarea>
            </div>
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
        if (id.length > 10) {
            vueVm.registered_components['prompts-params'].checkFields(id);
        } else {
            $(`#promptsParamsTable tr[data-uniqueid=${id}]`).find('textarea').each(function () {
                $(this).attr('disabled', 'disabled')
            })
            vueVm.registered_components['prompts-params'].updateField(id);
        }

    },
}