import SwiftUI
import AppleHealthSyncCore

struct ContentView: View {
    @StateObject private var model = AppModel()
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        NavigationStack {
            ScrollViewReader { proxy in
                Form {
                    Section {
                        TextField("https://home.example.com/api/webhook/…", text: $model.webhookURL)
                            .keyboardType(.URL)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()

                        SecureField("Optional shared secret", text: $model.secret)
                            .textContentType(.password)
                            .autocorrectionDisabled()

                        Toggle("Sync when the app opens", isOn: $model.syncOnOpen)
                    } header: {
                        Text("Home Assistant")
                    } footer: {
                        Text("Create a webhook under Settings → Devices & services → Apple Health Sync. The full URL is a credential; keep it private.")
                    }

                    Section {
                        HStack {
                            Text("Status")
                            Spacer()
                            Text(model.healthStatus)
                                .foregroundStyle(.secondary)
                        }

                        Button {
                            Task { await model.requestHealthAccess() }
                        } label: {
                            HStack {
                                Text("Request Health Access")
                                Spacer()
                                if model.isRequestingAccess {
                                    ProgressView()
                                }
                            }
                        }
                        .disabled(model.isRequestingAccess)

                        Toggle("Include additional HealthKit metrics", isOn: $model.includeExtras)
                    } header: {
                        Text("Apple Health")
                    } footer: {
                        Text("Read-only access. The app never writes to Apple Health. iOS does not reveal which read permissions were granted; if values are missing, check Settings → Privacy & Security → Health → Apple Health Sync. Changing the additional-metrics option requires requesting access again.")
                    }

                    Section {
                        Button {
                            Task { await model.sync() }
                        } label: {
                            HStack {
                                Spacer()
                                if model.isSyncing {
                                    ProgressView()
                                        .padding(.trailing, 6)
                                }
                                Text(model.isSyncing ? "Syncing…" : "Sync Now")
                                Spacer()
                            }
                        }
                        .disabled(model.isSyncing)

                        Button("Send a Test Payload") {
                            Task { await model.sendTestPayload() }
                        }
                        .disabled(model.isSyncing)
                    } header: {
                        Text("Sync")
                    } footer: {
                        Text("The test payload uses fixed sample values and works without HealthKit, including in the iOS simulator.")
                    }

                    Section {
                        Text(model.statusMessage)
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                            .textSelection(.enabled)

                        if let lastSync = model.lastSync {
                            HStack {
                                Text("Last successful sync")
                                Spacer()
                                Text(lastSync, format: .dateTime.day().month().year().hour().minute())
                                    .foregroundStyle(.secondary)
                            }
                            .font(.footnote)
                        }
                    } header: {
                        Text("Result")
                    }
                    .id("result")

                    Section("Latest Values") {
                        if model.readings.isEmpty {
                            Text("No values yet. Sync once to populate this list.")
                                .foregroundStyle(.secondary)
                        } else {
                            ForEach(model.readings) { reading in
                                HStack(alignment: .firstTextBaseline) {
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(reading.name)
                                        if !reading.canonical {
                                            Text("Additional metric")
                                                .font(.caption2)
                                                .foregroundStyle(.secondary)
                                        }
                                    }

                                    Spacer()

                                    Text(formatted(reading.value))
                                        .monospacedDigit()

                                    if let unit = reading.unit {
                                        Text(unit)
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                    }
                                }
                            }
                        }
                    }

                    Section {
                        Text("Apple Health Sync sends data directly to your Home Assistant instance. It has no analytics, no telemetry and no cloud service. The webhook URL and shared secret are stored in the iOS Keychain.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }
                .navigationTitle("Apple Health Sync")
                .onChange(of: model.webhookURL) { _, _ in model.saveSettings() }
                .onChange(of: model.secret) { _, _ in model.saveSettings() }
                .onChange(of: model.syncOnOpen) { _, _ in model.saveSettings() }
                .onChange(of: model.includeExtras) { _, _ in
                    model.saveSettings()
                    Task { await model.refreshHealthStatus() }
                }
                .onChange(of: model.lastSync) { _, newValue in
                    guard newValue != nil else { return }
                    withAnimation {
                        proxy.scrollTo("result", anchor: .top)
                    }
                }
                .task { await model.prepare() }
                .onChange(of: scenePhase) { _, newPhase in
                    if newPhase == .active {
                        Task { await model.syncOnLaunchIfNeeded() }
                    }
                }
            }
        }
    }

    private func formatted(_ value: Double) -> String {
        if value == value.rounded() {
            return String(Int(value))
        }
        return value.formatted(.number.precision(.fractionLength(0...2)))
    }
}

#Preview {
    ContentView()
}
