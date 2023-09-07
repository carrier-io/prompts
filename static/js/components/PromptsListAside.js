const PromptsListAside = {
    components: {
        ImportPromptButton
    },
    data() {
        return {
            loadingDelete: false,
        }
    },
    computed: {
        responsiveTableHeight() {
            return `${(window.innerHeight - 270)}px`;
        }
    },
    watch: {
    },
    methods: {
    },
    template: `
        <aside class="card card-table-sm" style="min-width: 340px; width: 340px">
            <div class="row p-4">
                <div class="col-4">
                    <p class="font-h4 font-bold">Prompts</p>
                </div>
                <div class="col-8">
                    <div class="d-flex justify-content-end">
                        <ImportPromptButton></ImportPromptButton>
                        <button type="button"
                            @click="$emit('open-create-modal')"
                            class="btn btn-basic btn-sm btn-icon__sm">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
            <div class="card-body" style="padding-top: 0">
                <table class="table table-borderless table-fix-thead"
                    id="prompts-aside-table"
                    data-toggle="table"
                    data-unique-id="id">
                    <thead class="thead-light bg-transparent">
                        <tr>
                            <th data-visible="false" data-field="id">index</th>
                            <th data-sortable="true" data-field="name" data-width="40" data-width-unit="%" >NAME</th>
                            <th scope="col" data-sortable="false" data-field="tags" data-formatter="ParamsTable.tagFormatter">Tags</th>
                            <th data-width="56" data-formatter='<div class="d-none justify-content-end">
                                    <button class="btn btn-default btn-xs btn-table btn-icon__xs prompt_delete"><i class="icon__18x18 icon-delete"></i></button>
                                </div>'
                                data-events="promptAsideEvents">
                            </th>
                        </tr>
                    </thead>
                    <tbody :style="{'height': responsiveTableHeight}">
                    </tbody>
                </table>
            </div>
        </aside>
    `
}

var promptAsideEvents = {
    "click .prompt_delete": function (e, value, row, index) {
        e.stopPropagation();
        const vm = vueVm.registered_components.prompts;
        vm.openConfirm();
    },
}
