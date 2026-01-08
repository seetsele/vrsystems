//
//  ContentView.swift
//  Verity - AI Fact Checker
//
//  Main Tab View with Premium Design
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        ZStack {
            // Animated Background
            AnimatedBackgroundView()
            
            // Main Tab View
            TabView(selection: $appState.selectedTab) {
                HomeView()
                    .tabItem {
                        Label("Home", systemImage: "house.fill")
                    }
                    .tag(AppState.Tab.home)
                
                VerifyView()
                    .tabItem {
                        Label("Verify", systemImage: "checkmark.shield.fill")
                    }
                    .tag(AppState.Tab.verify)
                
                HistoryView()
                    .tabItem {
                        Label("History", systemImage: "clock.fill")
                    }
                    .tag(AppState.Tab.history)
                
                ToolsView()
                    .tabItem {
                        Label("Tools", systemImage: "wrench.and.screwdriver.fill")
                    }
                    .tag(AppState.Tab.tools)
                
                SettingsView()
                    .tabItem {
                        Label("Settings", systemImage: "gearshape.fill")
                    }
                    .tag(AppState.Tab.settings)
            }
            .accentColor(.cyan)
        }
        .onAppear {
            setupTabBarAppearance()
            appState.loadStoredData()
        }
    }
    
    private func setupTabBarAppearance() {
        let appearance = UITabBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = UIColor(Color.black.opacity(0.95))
        
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
    }
}

// MARK: - Animated Background
struct AnimatedBackgroundView: View {
    @State private var animate = false
    
    var body: some View {
        ZStack {
            Color.black.edgesIgnoringSafeArea(.all)
            
            // Floating Orbs
            Circle()
                .fill(LinearGradient(colors: [.cyan.opacity(0.3), .clear], startPoint: .center, endPoint: .bottom))
                .frame(width: 400, height: 400)
                .blur(radius: 80)
                .offset(x: animate ? -50 : 50, y: animate ? -100 : 100)
            
            Circle()
                .fill(LinearGradient(colors: [.purple.opacity(0.25), .clear], startPoint: .center, endPoint: .bottom))
                .frame(width: 350, height: 350)
                .blur(radius: 70)
                .offset(x: animate ? 100 : -100, y: animate ? 150 : -50)
            
            Circle()
                .fill(LinearGradient(colors: [.pink.opacity(0.2), .clear], startPoint: .center, endPoint: .bottom))
                .frame(width: 300, height: 300)
                .blur(radius: 60)
                .offset(x: animate ? -80 : 80, y: animate ? 200 : 50)
            
            // Grid Overlay
            GridPattern()
                .stroke(Color.white.opacity(0.03), lineWidth: 0.5)
                .edgesIgnoringSafeArea(.all)
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 15).repeatForever(autoreverses: true)) {
                animate.toggle()
            }
        }
    }
}

struct GridPattern: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let spacing: CGFloat = 30
        
        for x in stride(from: 0, through: rect.width, by: spacing) {
            path.move(to: CGPoint(x: x, y: 0))
            path.addLine(to: CGPoint(x: x, y: rect.height))
        }
        
        for y in stride(from: 0, through: rect.height, by: spacing) {
            path.move(to: CGPoint(x: 0, y: y))
            path.addLine(to: CGPoint(x: rect.width, y: y))
        }
        
        return path
    }
}

// MARK: - Home View
struct HomeView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Header Card
                    VStack(spacing: 16) {
                        HStack {
                            Image(systemName: "shield.checkered")
                                .font(.system(size: 44))
                                .foregroundStyle(
                                    LinearGradient(colors: [.cyan, .purple, .pink], startPoint: .topLeading, endPoint: .bottomTrailing)
                                )
                            
                            Spacer()
                            
                            VStack(alignment: .trailing) {
                                Text("Connected")
                                    .font(.caption)
                                    .foregroundColor(.green)
                                HStack(spacing: 4) {
                                    Circle()
                                        .fill(.green)
                                        .frame(width: 8, height: 8)
                                    Text("Desktop Paired")
                                        .font(.caption2)
                                        .foregroundColor(.secondary)
                                }
                            }
                        }
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Welcome to Verity")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text("AI-Powered Fact Checking")
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .padding(20)
                    .background(GlassBackground())
                    .cornerRadius(20)
                    
                    // Stats Grid
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                        StatCard(title: "Verified", value: "\(appState.verificationHistory.filter { $0.score >= 70 }.count)", icon: "checkmark.circle.fill", color: .green)
                        StatCard(title: "Flagged", value: "\(appState.verificationHistory.filter { $0.score < 70 }.count)", icon: "exclamationmark.triangle.fill", color: .orange)
                        StatCard(title: "Total", value: "\(appState.verificationHistory.count)", icon: "chart.bar.fill", color: .cyan)
                        StatCard(title: "Accuracy", value: "98%", icon: "target", color: .purple)
                    }
                    
                    // Quick Actions
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Quick Actions")
                            .font(.headline)
                        
                        QuickActionButton(title: "Verify Claim", subtitle: "Check any statement", icon: "checkmark.shield", color: .cyan) {
                            appState.selectedTab = .verify
                        }
                        
                        QuickActionButton(title: "Check Source", subtitle: "Evaluate credibility", icon: "link.circle", color: .purple) {
                            appState.selectedTab = .tools
                        }
                        
                        QuickActionButton(title: "View History", subtitle: "Past verifications", icon: "clock.arrow.circlepath", color: .pink) {
                            appState.selectedTab = .history
                        }
                    }
                    .padding(20)
                    .background(GlassBackground())
                    .cornerRadius(20)
                    
                    // Recent Activity
                    if !appState.verificationHistory.isEmpty {
                        VStack(alignment: .leading, spacing: 16) {
                            Text("Recent Activity")
                                .font(.headline)
                            
                            ForEach(appState.verificationHistory.prefix(3)) { result in
                                HistoryRow(result: result)
                            }
                        }
                        .padding(20)
                        .background(GlassBackground())
                        .cornerRadius(20)
                    }
                }
                .padding()
            }
            .navigationTitle("Home")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

// MARK: - Verify View
struct VerifyView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var networkService: NetworkService
    @State private var claimText = ""
    @State private var deepAnalysis = true
    @State private var result: VerificationResult?
    @State private var showingResult = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Input Section
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Enter Claim to Verify")
                            .font(.headline)
                        
                        TextEditor(text: $claimText)
                            .frame(minHeight: 120)
                            .padding(12)
                            .background(Color.white.opacity(0.05))
                            .cornerRadius(12)
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
                            )
                        
                        Toggle(isOn: $deepAnalysis) {
                            HStack {
                                Image(systemName: "brain")
                                    .foregroundColor(.purple)
                                Text("Deep AI Analysis")
                            }
                        }
                        .tint(.cyan)
                        
                        Button(action: verifyClaim) {
                            HStack {
                                if networkService.isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Image(systemName: "checkmark.shield.fill")
                                }
                                Text(networkService.isLoading ? "Analyzing..." : "Verify Claim")
                                    .fontWeight(.semibold)
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                LinearGradient(colors: [.cyan, .purple], startPoint: .leading, endPoint: .trailing)
                            )
                            .foregroundColor(.white)
                            .cornerRadius(12)
                        }
                        .disabled(claimText.isEmpty || networkService.isLoading)
                    }
                    .padding(20)
                    .background(GlassBackground())
                    .cornerRadius(20)
                    
                    // Result Section
                    if let result = result {
                        ResultCard(result: result)
                    }
                    
                    // How It Works
                    VStack(alignment: .leading, spacing: 16) {
                        Text("How It Works")
                            .font(.headline)
                        
                        HowItWorksStep(number: 1, title: "Enter Claim", description: "Paste any statement, headline, or quote", icon: "text.quote")
                        HowItWorksStep(number: 2, title: "AI Analysis", description: "Our models analyze from multiple sources", icon: "cpu")
                        HowItWorksStep(number: 3, title: "Get Results", description: "Receive accuracy score and sources", icon: "checkmark.seal")
                    }
                    .padding(20)
                    .background(GlassBackground())
                    .cornerRadius(20)
                }
                .padding()
            }
            .navigationTitle("Verify")
            .navigationBarTitleDisplayMode(.large)
        }
    }
    
    private func verifyClaim() {
        Task {
            do {
                let verificationResult = try await networkService.verifyClaim(claimText, deepAnalysis: deepAnalysis)
                await MainActor.run {
                    result = verificationResult
                    appState.verificationHistory.insert(verificationResult, at: 0)
                    appState.saveHistory()
                }
            } catch {
                print("Verification error: \(error)")
            }
        }
    }
}

// MARK: - History View
struct HistoryView: View {
    @EnvironmentObject var appState: AppState
    @State private var searchText = ""
    @State private var selectedFilter: FilterOption = .all
    
    enum FilterOption: String, CaseIterable {
        case all = "All"
        case verified = "Verified"
        case flagged = "Flagged"
    }
    
    var filteredHistory: [VerificationResult] {
        appState.verificationHistory.filter { result in
            let matchesSearch = searchText.isEmpty || result.claim.localizedCaseInsensitiveContains(searchText)
            let matchesFilter: Bool
            switch selectedFilter {
            case .all: matchesFilter = true
            case .verified: matchesFilter = result.score >= 70
            case .flagged: matchesFilter = result.score < 70
            }
            return matchesSearch && matchesFilter
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Filter Pills
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        ForEach(FilterOption.allCases, id: \.self) { option in
                            FilterPill(title: option.rawValue, isSelected: selectedFilter == option) {
                                selectedFilter = option
                            }
                        }
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 12)
                }
                
                if filteredHistory.isEmpty {
                    Spacer()
                    VStack(spacing: 16) {
                        Image(systemName: "clock.badge.questionmark")
                            .font(.system(size: 60))
                            .foregroundColor(.secondary)
                        Text("No History Yet")
                            .font(.title2)
                            .fontWeight(.semibold)
                        Text("Your verified claims will appear here")
                            .foregroundColor(.secondary)
                    }
                    Spacer()
                } else {
                    List {
                        ForEach(filteredHistory) { result in
                            HistoryRow(result: result)
                                .listRowBackground(Color.clear)
                                .listRowSeparator(.hidden)
                        }
                        .onDelete(perform: deleteItems)
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("History")
            .navigationBarTitleDisplayMode(.large)
            .searchable(text: $searchText, prompt: "Search history")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { appState.verificationHistory.removeAll(); appState.saveHistory() }) {
                        Image(systemName: "trash")
                    }
                }
            }
        }
    }
    
    private func deleteItems(at offsets: IndexSet) {
        appState.verificationHistory.remove(atOffsets: offsets)
        appState.saveHistory()
    }
}

// MARK: - Tools View
struct ToolsView: View {
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 16) {
                    ToolCard(
                        title: "Source Checker",
                        description: "Evaluate the credibility of any website or news source",
                        icon: "link.circle.fill",
                        color: .cyan
                    )
                    
                    ToolCard(
                        title: "Content Moderator",
                        description: "Detect harmful content, hate speech, and misinformation",
                        icon: "shield.fill",
                        color: .purple
                    )
                    
                    ToolCard(
                        title: "Research Assistant",
                        description: "AI-powered research from academic databases",
                        icon: "book.fill",
                        color: .pink
                    )
                    
                    ToolCard(
                        title: "Social Monitor",
                        description: "Track trending misinformation across platforms",
                        icon: "bell.badge.fill",
                        color: .orange
                    )
                    
                    ToolCard(
                        title: "Stats Validator",
                        description: "Verify statistical claims and data citations",
                        icon: "chart.bar.fill",
                        color: .green
                    )
                    
                    ToolCard(
                        title: "Realtime Stream",
                        description: "Live feed of fact-checks from around the world",
                        icon: "waveform",
                        color: .blue
                    )
                }
                .padding()
            }
            .navigationTitle("AI Tools")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

// MARK: - Settings View
struct SettingsView: View {
    @EnvironmentObject var appState: AppState
    @State private var notificationsEnabled = true
    @State private var deepAnalysisDefault = true
    @State private var saveHistory = true
    
    var body: some View {
        NavigationView {
            List {
                Section {
                    HStack(spacing: 16) {
                        Image(systemName: "person.circle.fill")
                            .font(.system(size: 60))
                            .foregroundStyle(
                                LinearGradient(colors: [.cyan, .purple], startPoint: .topLeading, endPoint: .bottomTrailing)
                            )
                        
                        VStack(alignment: .leading) {
                            Text(appState.user?.name ?? "Guest User")
                                .font(.title2)
                                .fontWeight(.semibold)
                            Text(appState.isPremium ? "Pro Plan" : "Free Plan")
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.vertical, 8)
                } header: {
                    Text("Account")
                }
                .listRowBackground(GlassBackground())
                
                Section {
                    SettingsToggle(title: "Push Notifications", icon: "bell.fill", isOn: $notificationsEnabled)
                    SettingsToggle(title: "Deep Analysis Default", icon: "brain", isOn: $deepAnalysisDefault)
                    SettingsToggle(title: "Save History", icon: "clock.fill", isOn: $saveHistory)
                } header: {
                    Text("Preferences")
                }
                .listRowBackground(GlassBackground())
                
                Section {
                    LanguageSettingRow()
                    SettingsToggle(title: "Auto-Translate Claims", icon: "globe", isOn: $appState.autoTranslate)
                } header: {
                    Text("Language")
                }
                .listRowBackground(GlassBackground())
                
                Section {
                    SettingsLink(title: "Desktop Pairing", icon: "desktopcomputer", color: .cyan)
                    SettingsLink(title: "API Keys", icon: "key.fill", color: .purple)
                    NavigationLink(destination: ExportSettingsView()) {
                        SettingsRowContent(title: "Export Data", icon: "square.and.arrow.up", color: .green)
                    }
                    NavigationLink(destination: WebhooksSettingsView()) {
                        SettingsRowContent(title: "Webhooks", icon: "bolt.horizontal.fill", color: .orange)
                    }
                } header: {
                    Text("Sync & Data")
                }
                .listRowBackground(GlassBackground())
                
                Section {
                    NavigationLink(destination: AnalyticsView()) {
                        SettingsRowContent(title: "Analytics", icon: "chart.pie.fill", color: .indigo)
                    }
                } header: {
                    Text("Insights")
                }
                .listRowBackground(GlassBackground())
                
                Section {
                    SettingsLink(title: "Help Center", icon: "questionmark.circle.fill", color: .blue)
                    SettingsLink(title: "Privacy Policy", icon: "hand.raised.fill", color: .orange)
                    SettingsLink(title: "Terms of Service", icon: "doc.text.fill", color: .gray)
                } header: {
                    Text("Support")
                }
                .listRowBackground(GlassBackground())
                
                Section {
                    VStack(spacing: 8) {
                        Text("Verity for iOS")
                            .fontWeight(.semibold)
                        Text("Version 2.0.0")
                            .foregroundColor(.secondary)
                            .font(.caption)
                        Text("© 2024 Verity Systems")
                            .foregroundColor(.secondary)
                            .font(.caption2)
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                }
                .listRowBackground(Color.clear)
            }
            .scrollContentBackground(.hidden)
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

// MARK: - Reusable Components
struct GlassBackground: View {
    var body: some View {
        RoundedRectangle(cornerRadius: 16)
            .fill(Color.white.opacity(0.05))
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(value)
                .font(.title)
                .fontWeight(.bold)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(GlassBackground())
        .cornerRadius(16)
    }
}

struct QuickActionButton: View {
    let title: String
    let subtitle: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                    .frame(width: 44, height: 44)
                    .background(color.opacity(0.2))
                    .cornerRadius(12)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color.white.opacity(0.03))
            .cornerRadius(12)
        }
    }
}

struct HistoryRow: View {
    let result: VerificationResult
    
    var body: some View {
        HStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(result.scoreCategory.color.opacity(0.2))
                    .frame(width: 50, height: 50)
                
                Text("\(result.score)")
                    .font(.headline)
                    .fontWeight(.bold)
                    .foregroundColor(result.scoreCategory.color)
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(result.claim)
                    .lineLimit(2)
                    .font(.subheadline)
                
                HStack {
                    Text(result.scoreCategory.label)
                        .font(.caption)
                        .foregroundColor(result.scoreCategory.color)
                    
                    Text("•")
                        .foregroundColor(.secondary)
                    
                    Text(result.timestamp, style: .relative)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
        }
        .padding()
        .background(GlassBackground())
        .cornerRadius(12)
    }
}

struct ResultCard: View {
    let result: VerificationResult
    
    var body: some View {
        VStack(spacing: 20) {
            // Score Circle
            ZStack {
                Circle()
                    .stroke(result.scoreCategory.color.opacity(0.3), lineWidth: 10)
                    .frame(width: 100, height: 100)
                
                Circle()
                    .trim(from: 0, to: CGFloat(result.score) / 100)
                    .stroke(result.scoreCategory.color, style: StrokeStyle(lineWidth: 10, lineCap: .round))
                    .frame(width: 100, height: 100)
                    .rotationEffect(.degrees(-90))
                
                VStack {
                    Text("\(result.score)")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                    Text(result.scoreCategory.label)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            // Verdict
            Text(result.verdict)
                .font(.title2)
                .fontWeight(.semibold)
            
            Text(result.explanation)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
            
            // Sources
            VStack(alignment: .leading, spacing: 8) {
                Text("Sources (\(result.sources.count))")
                    .font(.headline)
                
                ForEach(result.sources) { source in
                    HStack {
                        Image(systemName: "link")
                            .foregroundColor(.cyan)
                        Text(source.name)
                        Spacer()
                        Text("\(source.credibilityScore)%")
                            .foregroundColor(.green)
                    }
                    .font(.caption)
                    .padding(8)
                    .background(Color.white.opacity(0.03))
                    .cornerRadius(8)
                }
            }
        }
        .padding(24)
        .background(GlassBackground())
        .cornerRadius(20)
    }
}

struct HowItWorksStep: View {
    let number: Int
    let title: String
    let description: String
    let icon: String
    
    var body: some View {
        HStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(Color.cyan.opacity(0.2))
                    .frame(width: 44, height: 44)
                
                Image(systemName: icon)
                    .foregroundColor(.cyan)
            }
            
            VStack(alignment: .leading, spacing: 2) {
                Text("Step \(number): \(title)")
                    .fontWeight(.semibold)
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding()
        .background(Color.white.opacity(0.03))
        .cornerRadius(12)
    }
}

struct FilterPill: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .fontWeight(.medium)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? Color.cyan : Color.white.opacity(0.1))
                .foregroundColor(isSelected ? .black : .white)
                .cornerRadius(20)
        }
    }
}

struct ToolCard: View {
    let title: String
    let description: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(color)
                .frame(width: 56, height: 56)
                .background(color.opacity(0.2))
                .cornerRadius(14)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
        }
        .padding()
        .background(GlassBackground())
        .cornerRadius(16)
    }
}

struct SettingsToggle: View {
    let title: String
    let icon: String
    var isOn: Binding<Bool>
    
    var body: some View {
        Toggle(isOn: isOn) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(.cyan)
                Text(title)
            }
        }
        .tint(.cyan)
    }
}

struct SettingsLink: View {
    let title: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(color)
            Text(title)
            Spacer()
            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
        }
    }
}

struct SettingsRowContent: View {
    let title: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(color)
            Text(title)
        }
    }
}

// MARK: - Language Setting Row
struct LanguageSettingRow: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        HStack {
            Image(systemName: "globe")
                .foregroundColor(.cyan)
            Text("Language")
            Spacer()
            Menu {
                ForEach(["English", "Spanish", "French", "German", "Chinese", "Japanese", "Arabic"], id: \.self) { lang in
                    Button(lang) {
                        appState.selectedLanguage = lang
                    }
                }
            } label: {
                HStack(spacing: 4) {
                    Text(appState.selectedLanguage)
                        .foregroundColor(.secondary)
                    Image(systemName: "chevron.up.chevron.down")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
    }
}

// MARK: - Analytics View
struct AnalyticsView: View {
    @EnvironmentObject var appState: AppState
    
    var verifiedCount: Int {
        appState.verificationHistory.filter { $0.score >= 70 }.count
    }
    
    var falseCount: Int {
        appState.verificationHistory.filter { $0.score < 70 }.count
    }
    
    var averageScore: Double {
        guard !appState.verificationHistory.isEmpty else { return 0 }
        return Double(appState.verificationHistory.reduce(0) { $0 + $1.score }) / Double(appState.verificationHistory.count)
    }
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Overview Stats
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 16) {
                    AnalyticsStatCard(title: "Total Verified", value: "\(appState.verificationHistory.count)", color: .cyan)
                    AnalyticsStatCard(title: "True Claims", value: "\(verifiedCount)", color: .green)
                    AnalyticsStatCard(title: "False Claims", value: "\(falseCount)", color: .red)
                    AnalyticsStatCard(title: "Avg Score", value: String(format: "%.0f%%", averageScore), color: .purple)
                }
                
                // Score Distribution
                VStack(alignment: .leading, spacing: 16) {
                    Text("Score Distribution")
                        .font(.headline)
                    
                    VStack(spacing: 8) {
                        ScoreDistributionRow(label: "90-100%", count: appState.verificationHistory.filter { $0.score >= 90 }.count, total: appState.verificationHistory.count, color: .green)
                        ScoreDistributionRow(label: "70-89%", count: appState.verificationHistory.filter { $0.score >= 70 && $0.score < 90 }.count, total: appState.verificationHistory.count, color: .yellow)
                        ScoreDistributionRow(label: "50-69%", count: appState.verificationHistory.filter { $0.score >= 50 && $0.score < 70 }.count, total: appState.verificationHistory.count, color: .orange)
                        ScoreDistributionRow(label: "0-49%", count: appState.verificationHistory.filter { $0.score < 50 }.count, total: appState.verificationHistory.count, color: .red)
                    }
                }
                .padding(20)
                .background(GlassBackground())
                .cornerRadius(20)
                
                // Activity Timeline
                VStack(alignment: .leading, spacing: 16) {
                    Text("Recent Activity")
                        .font(.headline)
                    
                    if appState.verificationHistory.isEmpty {
                        Text("No verifications yet")
                            .foregroundColor(.secondary)
                            .padding()
                    } else {
                        ForEach(appState.verificationHistory.prefix(5)) { result in
                            HStack {
                                Circle()
                                    .fill(result.scoreCategory.color)
                                    .frame(width: 10, height: 10)
                                Text(result.claim)
                                    .lineLimit(1)
                                    .font(.caption)
                                Spacer()
                                Text("\(result.score)%")
                                    .font(.caption)
                                    .fontWeight(.semibold)
                                    .foregroundColor(result.scoreCategory.color)
                            }
                        }
                    }
                }
                .padding(20)
                .background(GlassBackground())
                .cornerRadius(20)
            }
            .padding()
        }
        .navigationTitle("Analytics")
        .navigationBarTitleDisplayMode(.large)
    }
}

struct AnalyticsStatCard: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Text(value)
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(color)
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(GlassBackground())
        .cornerRadius(16)
    }
}

struct ScoreDistributionRow: View {
    let label: String
    let count: Int
    let total: Int
    let color: Color
    
    var percentage: Double {
        guard total > 0 else { return 0 }
        return Double(count) / Double(total)
    }
    
    var body: some View {
        HStack {
            Text(label)
                .font(.caption)
                .frame(width: 60, alignment: .leading)
            
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.white.opacity(0.1))
                    RoundedRectangle(cornerRadius: 4)
                        .fill(color)
                        .frame(width: geo.size.width * percentage)
                }
            }
            .frame(height: 20)
            
            Text("\(count)")
                .font(.caption)
                .fontWeight(.semibold)
                .frame(width: 30, alignment: .trailing)
        }
    }
}

// MARK: - Export Settings View
struct ExportSettingsView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedFormat: ExportFormat = .json
    @State private var includeMetadata = true
    @State private var showingExportAlert = false
    
    enum ExportFormat: String, CaseIterable {
        case json = "JSON"
        case csv = "CSV"
        case pdf = "PDF"
    }
    
    var body: some View {
        List {
            Section {
                ForEach(ExportFormat.allCases, id: \.self) { format in
                    HStack {
                        Image(systemName: format == .json ? "curlybraces" : format == .csv ? "tablecells" : "doc.fill")
                            .foregroundColor(.cyan)
                        Text(format.rawValue)
                        Spacer()
                        if selectedFormat == format {
                            Image(systemName: "checkmark")
                                .foregroundColor(.cyan)
                        }
                    }
                    .contentShape(Rectangle())
                    .onTapGesture {
                        selectedFormat = format
                    }
                }
            } header: {
                Text("Export Format")
            }
            .listRowBackground(GlassBackground())
            
            Section {
                Toggle(isOn: $includeMetadata) {
                    HStack {
                        Image(systemName: "info.circle")
                            .foregroundColor(.purple)
                        Text("Include Metadata")
                    }
                }
                .tint(.cyan)
            } header: {
                Text("Options")
            }
            .listRowBackground(GlassBackground())
            
            Section {
                Button(action: {
                    exportData()
                }) {
                    HStack {
                        Image(systemName: "square.and.arrow.up")
                        Text("Export Now")
                        Spacer()
                        Text("\(appState.verificationHistory.count) items")
                            .foregroundColor(.secondary)
                    }
                }
                .foregroundColor(.cyan)
            }
            .listRowBackground(GlassBackground())
        }
        .scrollContentBackground(.hidden)
        .navigationTitle("Export Data")
        .navigationBarTitleDisplayMode(.large)
        .alert("Export Complete", isPresented: $showingExportAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("Your data has been exported as \(selectedFormat.rawValue)")
        }
    }
    
    private func exportData() {
        // Implementation would connect to the API
        showingExportAlert = true
    }
}

// MARK: - Webhooks Settings View
struct WebhooksSettingsView: View {
    @State private var webhooks: [WebhookItem] = []
    @State private var showingAddSheet = false
    @State private var newWebhookURL = ""
    @State private var newWebhookEvent = "verification.complete"
    
    struct WebhookItem: Identifiable {
        let id = UUID()
        var url: String
        var event: String
        var isActive: Bool
    }
    
    var body: some View {
        List {
            Section {
                ForEach($webhooks) { $webhook in
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: "bolt.horizontal.fill")
                                .foregroundColor(webhook.isActive ? .green : .gray)
                            Text(webhook.event)
                                .font(.subheadline)
                                .fontWeight(.semibold)
                            Spacer()
                            Toggle("", isOn: $webhook.isActive)
                                .labelsHidden()
                                .tint(.cyan)
                        }
                        Text(webhook.url)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    }
                    .padding(.vertical, 4)
                }
                .onDelete(perform: deleteWebhook)
            } header: {
                Text("Active Webhooks")
            } footer: {
                Text("Webhooks send POST requests when events occur")
            }
            .listRowBackground(GlassBackground())
            
            Section {
                Button(action: { showingAddSheet = true }) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Add Webhook")
                    }
                    .foregroundColor(.cyan)
                }
            }
            .listRowBackground(GlassBackground())
        }
        .scrollContentBackground(.hidden)
        .navigationTitle("Webhooks")
        .navigationBarTitleDisplayMode(.large)
        .sheet(isPresented: $showingAddSheet) {
            AddWebhookSheet(webhooks: $webhooks, isPresented: $showingAddSheet)
        }
    }
    
    private func deleteWebhook(at offsets: IndexSet) {
        webhooks.remove(atOffsets: offsets)
    }
}

struct AddWebhookSheet: View {
    @Binding var webhooks: [WebhooksSettingsView.WebhookItem]
    @Binding var isPresented: Bool
    @State private var url = ""
    @State private var selectedEvent = "verification.complete"
    
    let events = ["verification.complete", "verification.failed", "export.ready", "daily.summary"]
    
    var body: some View {
        NavigationView {
            Form {
                Section {
                    TextField("Webhook URL", text: $url)
                        .keyboardType(.URL)
                        .autocapitalization(.none)
                } header: {
                    Text("URL")
                }
                
                Section {
                    Picker("Event", selection: $selectedEvent) {
                        ForEach(events, id: \.self) { event in
                            Text(event).tag(event)
                        }
                    }
                } header: {
                    Text("Trigger Event")
                }
            }
            .navigationTitle("Add Webhook")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { isPresented = false }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Add") {
                        let newWebhook = WebhooksSettingsView.WebhookItem(url: url, event: selectedEvent, isActive: true)
                        webhooks.append(newWebhook)
                        isPresented = false
                    }
                    .disabled(url.isEmpty)
                }
            }
        }
    }
}

// MARK: - Preview
#Preview {
    ContentView()
        .environmentObject(AppState())
        .environmentObject(NetworkService())
}

