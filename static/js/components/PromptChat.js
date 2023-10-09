const PromptChat = {
    props: ['selectedPrompt', 'editablePrompt', 'isPromptLoading', 'isLatestVersion', 'testInput', 'testOutput', 'isRunLoading'],
    computed: {
        isDisableAddButton() {
            return !this.testOutput[0].content || !this.testInput ||
                this.testOutput[0].type === 'image' || this.testOutput.length > 1;
        },
    },
    methods: {
        addEmptyParamsRow()  {
            this.editablePrompt.examples.push({
                id: Date.now() + Math.floor(Math.random() * 1000),
                input: '',
                output: '',
            })
        },
        changeCbxExample(id, { target: { checked }}) {
            vueVm.registered_components['prompts-params'].updateField(id, checked);
        }
    },
    template: `
        <div class="flex-grow-1">
            <div class="card mt-3 p-28">
                <p class="font-h6 font-bold text-gray-800" style="color: #32325D">CONVERSATION</p>
                <div class="position-relative" style="height: 116px" v-show="isPromptLoading">
                    <div class="layout-spinner">
                        <div class="spinner-centered">
                            <i class="spinner-loader__32x32"></i>
                        </div>
                    </div>
                </div>
                <div v-show="!isPromptLoading" class="mt-4">
                    <div class="d-flex gap-3 align-items-center border-top py-2" v-for="example in editablePrompt.examples">
                        <div class="d-flex justify-content-center w-12">
                            <label class="mb-0 d-flex align-items-center custom-checkbox">
                                <input 
                                    type="checkbox" 
                                    @change="changeCbxExample(example.id, $event)">
                            </label>
                        </div>
                        <div class="flex-grow-1">
                            <div class="d-flex gap-3 align-items-center mb-2">
                                <p class="font-h6 font-weight-600 w-12 text-gray-600">USER</p>
                                <div class="custom-input w-100">
                                    <input type="text" class="form-control">
                                </div>
                            </div>
                            <div class="d-flex gap-3 align-items-center">
                                <p class="font-h6 font-weight-600 w-12">AI</p>
                                <div class="custom-input w-100">
                                    <input type="text" class="form-control">
                                </div>
                            </div>
                        </div>
                        <button type="button" class="btn btn-default btn-xs btn-table btn-icon__xs ml-1">
                            <i class="icon__18x18 icon-delete"></i>
                        </button>
                    </div>
                    <div class="pt-2" :class="{ 'border-top': editablePrompt.examples.length }">
                        <button type="button" class="btn btn-sm btn-secondary mt-2"
                            :disabled="!isLatestVersion"
                            @click="addEmptyParamsRow">
                            <i class="fas fa-plus mr-2"></i>Example
                        </button>
                    </div>
                </div>
            </div>
            <div class="card mt-3 p-28">
                <div class="d-flex justify-content-between mb-2">
                    <div class="d-flex align-items-center">
                        <p class="font-h6 font-bold text-gray-800 mr-4" style="color: #32325D">CHAT</p>
                    </div>
                    <div class="d-flex">
                        <p class="font-h5 text-gray-500 cursor-pointer">Clear conversation</p>
                    </div>
                </div>
                <div class="position-relative" style="height: 188px" v-if="isPromptLoading">
                    <div class="layout-spinner">
                        <div class="spinner-centered">
                            <i class="spinner-loader__32x32"></i>
                        </div>
                    </div>
                </div>
                <div v-else>
                    <div contenteditable class="prompt-chat">
                        <div class="d-flex gap-3 align-items-start">
                            <p class="font-h6 font-weight-600 w-20 p-3 text-gray-600">USER</p>
                            <div class="p-3">
                                Arcu id pellentesque amet commodo aenean magna penatibus pellentesque facilisi. Ullamcorper sem morbi sit ante lorem.
                            </div>
                        </div>
                        <div class="d-flex gap-3 align-items-start rounded-sm" style="background: #F9FAFF">
                            <p class="font-h6 font-weight-600 w-20 p-3" style="color: var(--basic)">AI</p>
                            <div class="p-3">
                                Arcu id pellentesque amet commodo aenean magna penatibus pellentesque facilisi. Ullamcorper sem morbi sit ante lorem.
                            </div>
                        </div>
                        <div class="d-flex gap-3 align-items-start">
                            <p class="font-h6 font-weight-600 w-20 p-3 text-gray-600">USER</p>
                            <div class="p-3">
                                Arcu id pellentesque amet commodo aenean magna penatibus pellentesque facilisi. Ullamcorper sem morbi sit ante lorem.
                            </div>
                        </div>
                        <div class="d-flex gap-3 align-items-start rounded-sm" style="background: #F9FAFF">
                            <p class="font-h6 font-weight-600 w-20 p-3" style="color: var(--basic)">AI</p>
                            <div class="p-3">
                                Arcu id pellentesque amet commodo aenean magna penatibus pellentesque facilisi. Ullamcorper sem morbi sit ante lorem.
                            </div>
                        </div>
                    </div>
                    <div class="d-flex prompt-input mt-2">
                        <input type="text" class="flex-grow-1 prompt-message" placeholder="Enter a prompt to start conversation">
                        <button type="button" :disabled="isRunLoading || isPromptLoading"
                            style="padding: 4px 8px 4px 8px;"
                            class="btn btn-basic d-flex align-items-center ml-2" @click="$emit('run-test')">
                            <i class="icon__white icon__14x14 icon-sent__message"></i>
                            <i v-if="isRunLoading" class="preview-loader__white ml-2"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `
}