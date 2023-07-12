const PromptsParams = {
    props: {
        selectedPrompt: {
            type: Object,
            default: {
                "name": "",
                "prompt": "",
                "examples": []
            }
        },
        integrations: [],
    },
    components: {
        PromptsVertexIntegration,
        PromptsOpenaiIntegration,
    },
    data() {
        return {
            editablePrompt: {
                name: "",
                prompt: "",
                examples: [],
                model_settings: {},
            },
            testInput: '',
            testOutput: '',
            isRunClicked: false,
            selectedIntegration: "",
            selectedComponentInt: "",
            isRunLoading: false,
        }
    },
    computed: {
        isInvalidContext() {
            return this.isRunClicked && !this.editablePrompt.prompt
        },
        isInvalidTestInput() {
            return this.isRunClicked && !this.testInput
        },
    },
    watch: {
        selectedPrompt: {
            handler: function (newVal, oldVal) {
                this.editablePrompt = Object.assign({}, newVal);

                if (newVal.model_settings) {
                    this.integrations.forEach(integration => {
                        if (integration.id === newVal.integration_id) {
                            this.selectedIntegration = integration.name;
                            this.selectedComponentInt = integration.name;
                            this.changeIntegration(integration.name)
                            this.$nextTick(() => {
                                $("#selectIntegration").val(integration.name).selectpicker('refresh')
                            })
                        }
                    })
                } else {
                    this.selectedComponentInt = "";
                    this.selectedIntegration = "";
                    this.$nextTick(() => {
                        $('#selectIntegration').val('').selectpicker('refresh');
                    })
                }
                this.testInput = newVal.test_input ? newVal.test_input : "";
                this.testOutput = '';
                this.isRunClicked = false;
            },
            deep: true
        },
        selectedIntegration: {
            handler: function (newVal, oldVal) {
                if (!newVal) return
                this.changeIntegration(newVal)
            },
            deep: true
        }
    },
    mounted() {
        $('#promptsParamsTable').bootstrapTable()
        $('#selectIntegration').selectpicker('refresh');
    },
    methods: {
        changeIntegration(newVal) {
            if (this.selectedPrompt.integration_id) {
                const existedInt = this.integrations
                    .find(integration => integration.name.toLowerCase() === newVal.toLowerCase())
                this.selectedComponentInt = newVal;
                if (existedInt.id === this.selectedPrompt.integration_id) {
                    this.editablePrompt.model_settings = { ...this.selectedPrompt.model_settings }
                    return;
                }
            }
            const integrationNames = this.integrations.map(integration => integration.name.toLowerCase());
            if (integrationNames.includes(newVal.toLowerCase())) {
                this.selectedComponentInt = newVal.toLowerCase();
            }
            this.editablePrompt.model_settings = this.integrations
                .find(integration => integration.name.toLowerCase() === newVal.toLowerCase()).settings

            this.selectedComponentInt = newVal;
        },
        addEmptyParamsRow()  {
            $('#promptsParamsTable').bootstrapTable(
                'append',
                {id: Date.now() + Math.floor(Math.random() * 1000),"input": "", "output": "", "action": ""}
            )
        },
        checkFields(rowId) {
            const row = $('#promptsParamsTable').bootstrapTable('getRowByUniqueId', rowId)
            if (row.input && row.output) {
                ApiCreateExample(this.editablePrompt.id, row.input, row.output).then(data => {
                    $(`#promptsParamsTable tr[data-uniqueid=${rowId}]`).attr("data-uniqueid",data.id);
                    showNotify('SUCCESS', `Input/Output saved.`);
                })
            }
        },
        updateField(rowId) {
            const row = $('#promptsParamsTable').bootstrapTable('getRowByUniqueId', rowId)
            ApiUpdateExampleField(this.editablePrompt.id, rowId, row.input, row.output).then(data => {
                showNotify('INFO', `Input/Output updated.`);
            })
        },
        runTest() {
            this.isRunClicked = true;
            const integrationId = this.integrations.find(integration => integration.name === this.selectedIntegration)
            if (this.editablePrompt.prompt && this.testInput && this.selectedIntegration) {
                this.isRunLoading = true;
                ApiRunTest(this.editablePrompt, this.testInput, integrationId.id, integrationId.project_id).then(data => {
                    this.testOutput = data;
                }).catch(err => {
                    showNotify('ERROR', err)
                }).finally(() => {
                    this.isRunLoading = false;
                })
            }
        },
        updatePrompt(e) {
            this.editablePrompt.prompt = e.target.value;
            ApiUpdatePrompt(this.editablePrompt).then(data => {
                showNotify('SUCCESS', `Context updated.`)
            });
        },
        saveSettings() {
            ApiUpdatePrompt(this.editablePrompt).then(data => {
                showNotify('SUCCESS', `Settings updated.`)
            });
        },
        updateSetting(settings) {
            const settingsKeys = ['temperature', 'top_k', 'top_p', 'model_name', 'max_decode_steps', 'max_tokens'];
            const selectedSetting = {};
            for (const setting in settings) {
                if (settingsKeys.includes(setting)) {
                    selectedSetting[setting] = settings[setting];
                }
            }
            this.editablePrompt.integration_settings = Object.assign({}, selectedSetting);
        },
        addTestResult() {
            const rowId = Date.now() + Math.floor(Math.random() * 1000)
            $('#promptsParamsTable').bootstrapTable(
                'append',
                {id: rowId,"input": this.testInput, "output": this.testOutput, "action": ""}
            )
            this.checkFields(rowId)
        },
        showError(value) {
            return this.isRunClicked ? value.length > 0 : true;
        },
        hasError(value) {
            return value.length > 0;
        },
        deleteExample(exampleId) {
            ApiDeleteExample(exampleId).then(data => {});
        },
    },
    template: `     
    <div class="d-flex">
        <div class="flex-grow-1 mr-3">
            <div class="card p-28">
            
                <div class="d-flex justify-content-between mb-2">
                    <p class="font-h5 font-bold font-uppercase">{{ editablePrompt.name }}</p>
                    <button type="button" class="btn btn-basic d-flex align-items-center" @click="runTest">Run
                        <i v-if="isRunLoading" class="preview-loader__white ml-2"></i>
                    </button>
                </div>
                <p class="font-h5 font-bold font-uppercase mb-2">CONTEXT</p>
                <div class="w-100">
                    <div class="custom-input w-100" 
                        :class="{ 'invalid-input': isInvalidContext }">
                        <textarea
                            :value="editablePrompt.prompt"
                            @change="updatePrompt"
                            class="form-control password-mask" rows="5" id="SecretUpdateValue"></textarea>
                    </div>
                </div>
            </div>    
            
            <div class="card mt-3 p-28">
                <p class="font-h5 font-bold font-uppercase">EXAMPLES</p>
                <div>
                    <table 
                        id="promptsParamsTable"
                        class="w-100 table-transparent mb-2 params-table"
                        data-toggle="table"
                        data-unique-id="id"
                    >
                        <thead class="thead-light">
                            <tr>
                                <th data-field="id" data-visible="false"></th>
                                <th data-field="input"
                                    data-formatter="ParamsTable.textareaFormatter"
                                >
                                    <span class="font-h6 font-semibold mr-2" style="color: var(--green)">Input</span>
                                    <span class="font-h5 font-weight-400 text-capitalize">Input condition or question.</span>
                                </th>
                                <th data-field="output"
                                    data-formatter="ParamsTable.textareaFormatter"
                                >
                                    <span class="font-h6 font-semibold mr-2" style="color: var(--basic)">Output</span>
                                    <span class="font-h5 font-weight-400 text-capitalize">Input expected result.</span>
                                </th>
                                <th data-width="56" data-width-unit="px" 
                                    data-field="action"
                                    data-formatter="ParamsTable.parametersDeleteFormatter"
                                ></th>
                            </tr>
                        </thead>
                        <tbody style="border-bottom: solid 1px #EAEDEF">
                        </tbody>
                    </table>
                    <button type="button" class="btn btn-sm btn-secondary mt-2" 
                        @click="addEmptyParamsRow">
                        <i class="fas fa-plus mr-2"></i>Add Parameter
                    </button>
                </div>
            </div>
            
            <div class="card mt-3 p-28">
                <div class="d-flex justify-content-between mb-2">
                    <p class="font-h5 font-bold font-uppercase">TESTS</p>
                    <button type="button" class="btn btn-basic d-flex align-items-center" @click="runTest">
                        Run
                        <i v-if="isRunLoading" class="preview-loader__white ml-2"></i>
                    </button>
                </div>
                <div>
                    <table 
                        class="w-100 table-transparent mb-2 params-table" 
                        id="testResult">
                        <thead class="thead-light">
                            <tr>
                                <th data-field="inputTest"
                                    >
                                    <span class="font-h6 font-semibold mr-2" style="color: var(--green)">Input</span>
                                    <span class="font-h5 font-weight-400 text-capitalize">Input condition or question.</span>
                                </th>
                                <th data-field="outputTest"
                                >
                                    <span class="font-h6 font-semibold mr-2" style="color: var(--basic)">Output</span>
                                    <span class="font-h5 font-weight-400 text-capitalize">Input expected result.</span>
                                </th>
                                <th data-width="56" data-width-unit="px" 
                                    data-field="action"
                                    data-formatter="ParamsTable.parametersDeleteFormatter"
                                ></th>
                            </tr>
                        </thead>
                        <tbody style="border-bottom: solid 1px #EAEDEF">
                            <tr>
                                <td class="p-2">
                                    <div class="custom-input" :class="{ 'invalid-input': isInvalidTestInput }">
                                        <textarea type="text" class="form-control form-control-alternative"
                                            rows="5"
                                            v-model="testInput">
                                        </textarea>
                                        <div class="invalid-tooltip invalid-tooltip-custom"></div>
                                    </div>
                                </td>
                                <td class="p-2">
                                    <div>
                                        <textarea disabled type="text"
                                            rows="5"
                                            style="color: var(--green)"
                                            v-model="testOutput"
                                            class="form-control form-control-alternative">
                                        </textarea>
                                        <div class="invalid-tooltip invalid-tooltip-custom"></div>
                                    </div>
                                </td>
                                <td style="width: 56px;" class="p-2">
                                    <button :disabled="!testOutput || !testInput" 
                                        class="btn btn-default btn-xs btn-table btn-icon__xs prompt_setting" @click="addTestResult">
                                        <i class="icon__14x14 icon-add-column"></i>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="card p-4" style="width: 340px">
            <div class="d-flex justify-content-between">
                <p class="font-h4 font-bold">Integration</p>
            </div>
            <div class="select-validation mt-4" :class="{'invalid-select': !showError(selectedIntegration)}">
                <p class="font-h5 font-semibold mb-1">Select integration</p>
                <select id="selectIntegration" class="selectpicker bootstrap-select__b bootstrap-select__b-sm" 
                    v-model="selectedIntegration"
                    data-style="btn">
                    <option v-for="integration in integrations" :value="integration.name">{{ integration.config.name }}</option>
                </select>
                <span class="select_error-msg">Integration is require.</span>
            </div>
            <PromptsVertexIntegration 
                :is-run-clicked="isRunClicked"
                :selected-prompt="editablePrompt"
                @update-setting="updateSetting"
                :key="selectedPrompt"
                v-if="selectedIntegration === 'vertex_ai'">
            </PromptsVertexIntegration>
            <PromptsOpenaiIntegration 
                :is-run-clicked="isRunClicked"
                :selected-prompt="editablePrompt"
                @update-setting="updateSetting"
                :key="selectedPrompt"
                v-if="selectedIntegration === 'open_ai'">
            </PromptsOpenaiIntegration>
        </div>
    </div>  
    `
}

register_component('prompts-params', PromptsParams);