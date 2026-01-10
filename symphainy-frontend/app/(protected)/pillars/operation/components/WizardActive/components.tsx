// WizardActive UI Components
"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Loader2, ArrowLeft, Send, CheckCircle, FileText, Share2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { WizardActiveUIProps, ChatTurn } from "./types";

export function WizardActiveUI({
  chatHistory,
  input,
  setInput,
  loading,
  error,
  draftSop,
  published,
  publishedSop,
  publishedWorkflow,
  onSend,
  onPublish,
  onBack,
}: WizardActiveUIProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Workflow Builder Wizard</h2>
          <p className="text-gray-600 mt-1">
            Interactive workflow and SOP generation
          </p>
        </div>
        <Button onClick={onBack} variant="outline">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="text-red-800">
              <strong>Error:</strong> {error}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Panel */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Workflow Builder Chat</CardTitle>
              <CardDescription>
                Describe your process and the wizard will help you build it
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Chat History */}
              <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
                {chatHistory.map((turn: ChatTurn, index: number) => (
                  <div
                    key={index}
                    className={`flex ${
                      turn.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        turn.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <ReactMarkdown className="prose prose-sm max-w-none">
                        {turn.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                      <div className="flex items-center">
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        Thinking...
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input Form */}
              <form onSubmit={onSend} className="flex space-x-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe your process or ask a question..."
                  disabled={loading}
                  className="flex-1"
                />
                <Button type="submit" disabled={loading || !input.trim()}>
                  <Send className="w-4 h-4" />
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Draft SOP Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Draft SOP
              </CardTitle>
              <CardDescription>
                Generated Standard Operating Procedure
              </CardDescription>
            </CardHeader>
            <CardContent>
              {draftSop ? (
                <div className="max-h-96 overflow-y-auto">
                  <ReactMarkdown className="prose prose-sm max-w-none">
                    {typeof draftSop === 'string' ? draftSop : JSON.stringify(draftSop, null, 2)}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="text-gray-500 text-center py-8">
                  No draft SOP yet. Start chatting to generate one!
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Publish Section */}
      {draftSop && !published && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center text-green-800">
              <CheckCircle className="w-5 h-5 mr-2" />
              Ready to Publish
            </CardTitle>
            <CardDescription className="text-green-700">
              Your workflow and SOP are ready to be published
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={onPublish}
              disabled={loading}
              className="bg-green-600 hover:bg-green-700"
            >
              <Share2 className="w-4 h-4 mr-2" />
              {loading ? "Publishing..." : "Publish Workflow & SOP"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Published Results */}
      {published && (publishedSop || publishedWorkflow) && (
        <div className="space-y-6">
          <div className="flex items-center">
            <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-xl font-semibold text-green-800">
              Successfully Published!
            </h3>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Published SOP */}
            {publishedSop && (
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center text-green-800">
                    <FileText className="w-5 h-5 mr-2" />
                    Published SOP
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="max-h-96 overflow-y-auto">
                    <ReactMarkdown className="prose prose-sm max-w-none">
                      {typeof publishedSop === 'string' ? publishedSop : JSON.stringify(publishedSop, null, 2)}
                    </ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Published Workflow */}
            {publishedWorkflow && (
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="flex items-center text-green-800">
                    <Share2 className="w-5 h-5 mr-2" />
                    Published Workflow
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="max-h-96 overflow-y-auto">
                    <ReactMarkdown className="prose prose-sm max-w-none">
                      {typeof publishedWorkflow === 'string' ? publishedWorkflow : JSON.stringify(publishedWorkflow, null, 2)}
                    </ReactMarkdown>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  Your workflow and SOP have been saved to the global session and are available in other pillars.
                </p>
                <Button onClick={onBack} variant="outline">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Return to Operations
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 