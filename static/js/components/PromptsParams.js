const PromptsParams = {
    props: {
        selectedPrompt: {
            type: Object,
            default: {
                "name": "",
                "prompt": "",
                "examples": [],
            }
        },
        integrations: {
            type: Array,
            default: [],
        },
        tags: [],
        isPromptLoading: false,
    },
    components: {
        PromptFreeform,
        PromptChat,
        PromptsVertexIntegration,
        PromptsOpenaiIntegration,
        PromptsAzureOpenaiIntegration,
        PromptsAiDialIntegration,
        PromptsTagsModal,
        PromptsEditorName,
        PromptsEditorField,
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
            testOutput: [{
                type: 'text',
                content: '',
            }],
            isRunClicked: false,
            selectedIntegration: "",
            filteredModels: [],
            selectedComponentInt: "",
            isRunLoading: false,
            isContextLoading: false,
            promptTags: [],
            showTagsModal: false,
            promptVersions: [],
            selectedPromptVersion: {
                id: null,
                version: 'latest',
            },
            newDescription: '',
            isVersionLoaded: false,
        }
    },
    computed: {
        isInvalidContext() {
            return this.isRunClicked && !this.editablePrompt.prompt
        },
        isLatestVersion() {
            return this.selectedPrompt.version === 'latest';
        },
        isDisableAddButton() {
            return !this.testOutput[0].content || !this.testInput ||
                this.testOutput[0].type === 'image' || this.testOutput.length > 1;
        },
        responsiveBarHeight() {
            return `${(window.innerHeight - 95)}px`;
        },
        responsiveContentHeight() {
            return `${(window.innerHeight - 155)}px`;
        }
    },
    watch: {
        selectedPrompt: {
            handler: function (newVal, oldVal) {
                this.editablePrompt = _.cloneDeep(newVal);
                if (newVal.integration_uid) {
                    this.integrations.forEach(integration => {
                        if (integration.uid === newVal.integration_uid) {
                            this.selectedIntegration = integration;
                            this.selectedComponentInt = integration.name;
                            this.changeIntegration(integration);
                            $("#selectIntegration").val(integration.config.name);
                        }
                    })
                } else {
                    this.selectedComponentInt = "";
                    this.selectedIntegration = "";
                }
                this.testInput = newVal.test_input ? newVal.test_input : "";
                this.testOutput = [{
                    type: 'text',
                    content: '',
                }];
                this.isRunClicked = false;
                this.fetchPromptTags(this.selectedPrompt.id);
                this.fetchPromptVersions(newVal.name);
                this.$nextTick(() => {
                    $("#selectIntegration").selectpicker('refresh');
                    $('#promptsParamsTable').bootstrapTable('load', this.editablePrompt.examples);
                    $('#variablesTable').bootstrapTable('load', this.editablePrompt.variables);
                })
            },
            deep: true
        },
        selectedIntegration: {
            handler: function (newVal, oldVal) {
                if (!newVal) return
                this.changeIntegration(newVal)
            },
            deep: true
        },
    },
    mounted() {
        $('#promptsParamsTable').bootstrapTable();
        $('#variablesTable').bootstrapTable();
    },
    methods: {
        selectPromptVersion({ target: { value }}) {
            this.selectedPromptVersion = this.promptVersions.find(v => v.id === +value);
        },
        fetchPromptTags(promptId) {
            fetchPromptTagsAPI(promptId).then((tags) => {
                this.promptTags = tags;
            })
        },
        fetchPromptVersions(promptName) {
            fetchPromptVersionsAPI(promptName).then((prompts) => {
                console.log(prompts)
                this.promptVersions = prompts.map(({ id, version }) => ({ id, version }));
                this.selectedPromptVersion = this.promptVersions.find(v => v.id === this.selectedPrompt.id);
            }).finally(() => {
                this.isVersionLoaded = true;
                setTimeout(() => {
                    if (this.selectedPromptVersion) {
                        $('#selectedPromptVersion').val(this.selectedPromptVersion.id);
                        $('#selectedPromptVersion').selectpicker('refresh');
                    }
                }, 0)
            })
        },
        changeIntegration(newVal) {
            this.filteredModels = this.filterModelsByType(newVal.settings.models, this.editablePrompt);
            if (this.selectedPrompt.integration_uid) {
                const existedInt = this.integrations
                    .find(integration => integration.uid === newVal.uid)
                this.selectedComponentInt = newVal.name;
                if (existedInt.uid === this.selectedPrompt.integration_uid) {
                    this.editablePrompt.model_settings = { ...this.selectedPrompt.model_settings }
                    return;
                }
            }
            this.editablePrompt.model_settings = this.integrations
                .find(integration => integration.uid === newVal.uid).settings;
            this.selectedComponentInt = newVal.name;
        },
        filterModelsByType(models, prompt) {
            try {
                if (prompt.type === 'freeform') {
                    return models.filter(model =>
                        model.capabilities.completion === true ||
                        model.capabilities.chat_completion === true
                    )
                }
                if (prompt.type === 'chat') {
                    return models.filter(model =>
                        model.capabilities.chat_completion === true
                    )
                }
            } catch (e) {
                return models;
            }
        },
        addEmptyParamsRow()  {
            $('#promptsParamsTable').bootstrapTable(
                'append',
                {id: Date.now() + Math.floor(Math.random() * 1000),"input": "", "output": "", "action": ""}
            )
        },
        addEmptyVariableRow(){
            $('#variablesTable').bootstrapTable(
                'append',
                {id: Date.now() + Math.floor(Math.random() * 1000),"name": "", "value": "", "action": ""}
            )
        },
        checkFields(rowId) {
            const row = $('#promptsParamsTable').bootstrapTable('getRowByUniqueId', rowId)
            if (row.input && row.output) {
                $(`#promptsParamsTable tr[data-uniqueid=${rowId}]`).find('textarea').each(function () {
                    $(this).attr('disabled', 'disabled');
                })
                ApiCreateExample(this.editablePrompt.id, row.input, row.output).then(newRow => {
                    $('#promptsParamsTable')
                        .bootstrapTable('removeByUniqueId', rowId)
                        .bootstrapTable('append', newRow );
                    showNotify('SUCCESS', `Input/Output saved.`);
                })
            }
        },
        checkVariableFields(rowId) {
            const row = $('#variablesTable').bootstrapTable('getRowByUniqueId', rowId)
            if (row.name && row.value) {
                $(`#variablesTable tr[data-uniqueid=${rowId}]`).find('textarea').each(function () {
                    $(this).attr('disabled', 'disabled');
                })
                ApiCreateVariable(this.editablePrompt.id, row.name, row.value).then(newRow => {
                    $('#variablesTable')
                        .bootstrapTable('removeByUniqueId', rowId)
                        .bootstrapTable('append', newRow);
                    showNotify('SUCCESS', `Variable saved.`);
                })
            }
        },
        updateField(rowId, isChecked = null) {
            const row = $('#promptsParamsTable').bootstrapTable('getRowByUniqueId', rowId);
            ApiUpdateExampleField(this.editablePrompt.id, rowId, row.input, row.output, isChecked ?? row.is_active).then(data => {
                if (this.isLatestVersion) {
                    $(`#promptsParamsTable tr[data-uniqueid=${rowId}]`).find('textarea').each(function () {
                        $(this).removeAttr("disabled");
                    })
                }
                showNotify('INFO', `Input/Output updated.`);
            })
        },
        updateVariableField(rowId) {
            const row = $('#variablesTable').bootstrapTable('getRowByUniqueId', rowId)
            ApiUpdateVariableField(this.editablePrompt.id, rowId, row.name, row.value).then(data => {
                $(`#variablesTable tr[data-uniqueid=${rowId}]`).find('textarea').each(function () {
                    $(this).removeAttr("disabled");
                })
                showNotify('INFO', `Variable updated.`);
            })
            .catch(err => {
                $(`#variablesTable tr[data-uniqueid=${rowId}]`).find('textarea').each(function () {
                    $(this).removeAttr("disabled");
                })
                showNotify("ERROR", err)
            })
        },
        runTest() {
            this.isRunClicked = true;
            const integrationId = this.integrations.find(integration => integration.uid === this.selectedIntegration.uid)
            const computedCondition = this.editablePrompt.is_active_input
                ? this.editablePrompt.prompt && this.testInput && this.selectedIntegration
                : this.editablePrompt.prompt && this.selectedIntegration;
            if (computedCondition) {
                this.isRunLoading = true;
                const computedInput = this.editablePrompt.is_active_input ? this.testInput : null;
                ApiRunTest(this.editablePrompt, computedInput, integrationId.uid).then(data => {
                    this.testOutput = data.messages;
                    this.testOutput.map(msg => {
                        if (msg.type === 'image') {
                            msg.content = `data:${msg.content.type};base64, ${msg.content.data}`;
                        }
                    })
                }).catch(err => {
                    showNotify('ERROR', err)
                }).finally(() => {
                    this.isRunLoading = false;
                })
            }
        },
        updatePrompt(e) {
            this.editablePrompt.prompt = e.target.value;
            this.isContextLoading= true;
            ApiUpdatePrompt(this.editablePrompt).then(data => {
                this.isContextLoading = false;
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
                {
                    id: rowId,
                    "input": this.testInput,
                    "output": this.testOutput[0].content,
                    "action": ""
                }
            )
            this.checkFields(rowId);
        },
        showError(value) {
            return this.isRunClicked ? value : true;
        },
        hasError(value) {
            return value.length > 0;
        },
        deleteExample(exampleId) {
            ApiDeleteExample(exampleId).then(() => {
                showNotify('SUCCESS', 'Example delete.');
            });
        },
        deleteVariable(varId) {
            ApiDeleteVariable(varId).then(() => {
                showNotify('SUCCESS', 'Variable delete.');
            });
        },
        updateTags(tags) {
            this.editablePrompt.tags = tags;
        },
        LoadVersion() {
            vueVm.registered_components['prompts'].FetchPromptById(this.selectedPromptVersion.id);
        },
        deleteVersion() {
            ApiDeletePrompt(this.selectedPromptVersion.id).then(data => {
                showNotify('SUCCESS', 'Version delete.');
                const latestVersionId = this.promptVersions.find(v => v.version === 'latest').id;
                vueVm.registered_components['prompts'].FetchPromptById(latestVersionId);
            });
        },
        updateCbxInput({ target: { checked }}) {
            this.editablePrompt.is_active_input = !checked;
            this.isRunClicked = false;
            const isActive = !checked ? 'enabled' : 'disabled';
            ApiUpdatePrompt(this.editablePrompt).then(data => {
                showNotify('INFO', `Input ${isActive}.`)
            });
        },
        changeTestInput({ target: { value }}) {
            this.testInput = value;
        }
    },
    template: `
    <div class="d-flex">
        <div class="flex-grow-1 mr-3">
            <div class="card p-28">
                <div class="d-flex justify-content-between mb-2">
                    <promptsEditorName
                        v-show="!isPromptLoading"
                        :key="selectedPrompt.id"
                        :editable-prompt="editablePrompt"
                        v-model="editablePrompt.name">
                    </promptsEditorName>
                    <div class="d-flex">
                        <a class="btn btn-secondary mr-2"
                            download
                            :class="{'disabled': isPromptLoading}"
                            :href="
                                $root.build_api_url('prompts', 'export_import') +
                                '/' + $root.project_id +
                                '/' + editablePrompt.id +
                                '?as_file=true'"
                        >
                            Export
                        </a>
                        <button type="button" :disabled="isPromptLoading"
                            class="btn btn-secondary mr-2" @click="$emit('open-create-version-modal')">
                            Save version
                        </button>
                        <button type="button" :disabled="isRunLoading || isPromptLoading"
                            v-if="selectedPrompt.type === 'freeform'"
                            class="btn btn-basic d-flex align-items-center" @click="runTest">
                            Run
                            <i v-if="isRunLoading" class="preview-loader__white ml-2"></i>
                        </button>
                    </div>
                </div>
                <div class="position-relative" style="height: 164px" v-show="isPromptLoading">
                    <div class="layout-spinner">
                        <div class="spinner-centered">
                            <i class="spinner-loader__32x32"></i>
                        </div>
                    </div>
                </div>
                <div v-show="!isPromptLoading">
                    <promptsEditorField
                        title="Description"
                        :key="selectedPrompt.id"
                        :editable-prompt="editablePrompt"
                        v-model="editablePrompt.description">
                    </promptsEditorField>
                    <div>
                        <p class="font-h6 font-bold text-gray-800 flex-grow-1 mb-1" style="color: #32325D">CONTEXT</p>
                        <div class="w-100">
                            <div class="custom-input w-100 position-relative"
                                :class="{ 'invalid-input': isInvalidContext }">
                                <textarea
                                    :disabled="isContextLoading || !isLatestVersion"
                                    :value="editablePrompt.prompt"
                                    @change="updatePrompt"
                                    class="form-control password-mask" rows="5" id="SecretUpdateValue"></textarea>
                                    <div class="spinner__right-bottom" v-if="isContextLoading">
                                        <i class="spinner-loader__16x16"></i>
                                    </div>
                            </div>
                        </div>
                    </div>
                    <div class="mt-3">
                        <p class="font-h6 font-bold text-gray-800" style="color: #32325D">VARIABLES</p>
                        <table
                            id="variablesTable"
                            class="w-100 table-transparent mb-2 params-table"
                            data-toggle="table"
                            data-unique-id="id"
                        >
                            <thead class="thead-light">
                                <tr>
                                    <th data-field="id" data-visible="false"></th>
                                    <th data-field="name"
                                        data-formatter="VariableTable.textareaFormatter"
                                    >
                                        <span class="font-h6 font-semibold text-gray-800">Name</span>
                                    </th>
                                    <th data-field="value"
                                        data-formatter="VariableTable.textareaFormatter"
                                    >
                                        <span class="font-h6 font-semibold text-gray-800">Value</span>
                                    </th>
                                    <th data-width="56" data-width-unit="px"
                                        data-field="action"
                                        data-formatter="VariableTable.deleteFormatter"
                                    ></th>
                                </tr>
                            </thead>
                            <tbody style="border-bottom: solid 1px #EAEDEF">
                            </tbody>
                        </table>
                        <button type="button" class="btn btn-sm btn-secondary mt-2"
                            :disabled="!isLatestVersion"
                            @click="addEmptyVariableRow">
                            <i class="fas fa-plus mr-2"></i>Add Variable
                        </button>
                    </div>
                </div>
            </div>
            <PromptFreeform
                v-show="editablePrompt.type === 'freeform'"
                :selectedPrompt="selectedPrompt"
                :isLatestVersion="isLatestVersion"
                :editablePrompt="editablePrompt"
                :isPromptLoading="isPromptLoading"
                :testOutput="testOutput"
                :testInput="testInput"
                :is-run-loading="isRunLoading"
                :is-run-clicked="isRunClicked"
                @run-test="runTest"
                @add-test-result="addTestResult"
                @change-test-input="changeTestInput"
                @update-cbx-input="updateCbxInput">
            </PromptFreeform>
            <PromptChat
                v-show="editablePrompt.type === 'chat'"
                :selectedPrompt="selectedPrompt"
                :isLatestVersion="isLatestVersion"
                :editablePrompt="editablePrompt"
                :isPromptLoading="isPromptLoading"
                :testOutput="testOutput"
                :integrations="integrations"
                :selectedIntegration="selectedIntegration"
                :testInput="testInput"
                @run-chat="isRunClicked = true"
                @update-cbx-input="updateCbxInput">
            </PromptChat>
        </div>
        <div class="card p-4" style="min-width: 340px" :style="{'height': responsiveBarHeight}">
            <div class="d-flex justify-content-between">
                <p class="font-h4 font-bold mb-4">Settings</p>
            </div>
            <div class="position-relative h-100" v-if="isPromptLoading">
                <div class="layout-spinner">
                    <div class="spinner-centered">
                        <i class="spinner-loader__32x32"></i>
                    </div>
                </div>
            </div>
            <div v-else :style="{'height': responsiveContentHeight}" style="overflow-y: scroll;">
                <div class="select-validation" v-if="isVersionLoaded">
                    <p class="font-h5 font-semibold mb-1">Select version</p>
                    <select id="selectedPromptVersion" class="selectpicker bootstrap-select__b displacement-ml-4 bootstrap-select__b-sm"
                        @change="selectPromptVersion"
                        data-style="btn">
                        <option v-for="version in promptVersions" :value="version.id">{{ version.version }}</option>
                    </select>
                    <div class="d-flex justify-content-between">
                        <button type="button"
                            class="btn btn-basic d-flex align-items-center justify-content-center mt-1 flex-grow-1 mr-1" @click="LoadVersion">
                            Load version
                        </button>
                        <button type="button"
                            :disabled="selectedPromptVersion.version === 'latest'"
                            class="btn btn-secondary d-flex align-items-center mt-1" @click="deleteVersion">
                            Delete version
                        </button>
                    </div>
                </div>
                <div class="d-flex mt-4 flex-column">
                    <div>
                        <span class="font-h6 font-bold mr-2">TAGS:</span>
                        <button class="btn btn-xs btn-painted mr-1 rounded-pill mb-1" v-for="tag in editablePrompt.tags"
                            :style="{'--text-color': tag.color, '--brd-color': tag.color}">{{tag.tag}}
                        </button>
                    </div>
                    <div class="d-flex mt-1">
                        <button type="button" class="btn btn-default btn-xs btn-icon__xs mr-2"
                            @click="showTagsModal = true">
                            <i class="icon__18x18 icon-edit" data-toggle="tooltip" data-placement="top" title="Edit tags"></i>
                        </button>
                        <p class="font-h5">Edit tags</p>
                    </div>
                </div>
                <div class="select-validation mt-4" :class="{'invalid-select': !showError(selectedIntegration)}">
                    <p class="font-h5 font-semibold mb-1">Select integration</p>
                    <select id="selectIntegration" class="selectpicker bootstrap-select__b displacement-ml-4 bootstrap-select__b-sm"
                        v-model="selectedIntegration"
                        data-style="btn">
                        <option v-for="integration in integrations" :value="integration">{{ integration.config.name }}</option>
                    </select>
                    <span class="input_error-msg">Integration is require.</span>
                </div>
                <PromptsVertexIntegration
                    :is-run-clicked="isRunClicked"
                    :selected-prompt="editablePrompt"
                    :filtered-models="filteredModels"
                    @update-setting="updateSetting"
                    :key="selectedIntegration.uid"
                    v-if="selectedIntegration.name === 'vertex_ai'">
                </PromptsVertexIntegration>
                <PromptsOpenaiIntegration
                    :is-run-clicked="isRunClicked"
                    :selected-prompt="editablePrompt"
                    :filtered-models="filteredModels"
                    @update-setting="updateSetting"
                    :key="selectedIntegration.uid"
                    v-if="selectedIntegration.name === 'open_ai'">
                </PromptsOpenaiIntegration>
                <PromptsAzureOpenaiIntegration
                    :is-run-clicked="isRunClicked"
                    :selected-prompt="editablePrompt"
                    :filtered-models="filteredModels"
                    @update-setting="updateSetting"
                    :key="selectedIntegration.uid"
                    v-if="selectedIntegration.name === 'open_ai_azure'">
                </PromptsAzureOpenaiIntegration>
                <PromptsAiDialIntegration
                    :is-run-clicked="isRunClicked"
                    :selected-prompt="editablePrompt"
                    :filtered-models="filteredModels"
                    @update-setting="updateSetting"
                    :key="selectedIntegration.uid"
                    v-if="selectedIntegration.name === 'ai_dial'">
                </PromptsAiDialIntegration>
                <transition>
                    <prompts-tags-modal
                        v-if="showTagsModal"
                        :prompt="editablePrompt"
                        @update-tags="updateTags"
                        @close-modal="showTagsModal = false"
                    >
                    </prompts-tags-modal>
                </transition>
            </div>
        </div>
    </div>
    `
}

register_component('prompts-params', PromptsParams);
