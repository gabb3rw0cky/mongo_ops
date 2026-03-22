'use client'
import { useCallback, useEffect, useRef, useState, ChangeEvent } from 'react';
import { signIn, useSession } from 'next-auth/react';
import {Dropdown, DropdownOption, Button, ProtectedInput, NumberInput, MongoTable, Card, SchemaItem} from "@/components/ui"
import {ErrorCallout, InputRow, EllipsesLoader} from "@/components/layout"

import { encryptPayload, decryptPayload } from "@/lib/crypto-server";

const 	EMPTY_OPTION	: DropdownOption	=	{ value: '', label: '' };
const	FONT_SIZE 	=	'12px';

type SessionUser = {
  token?: string;
};

type SessionShape = {
  user?: SessionUser;
};

const HOST = process.env.NEXT_PUBLIC_HOST || "";

export default function Home() {
	const { data: session } = useSession();
  	const auth_session = session as SessionShape | null;
	const token = auth_session?.user?.token;
	const socket_ref	=	useRef<WebSocket | null>(null)

	const	[ is_connected	, set_is_connected	] = useState<boolean>(false);
	const	[ loading		, set_loading		] = useState<boolean>(false);

	const	[ mongo_uri		, set_mongo_uri		] = useState<string>('');
	const	[ disable_uri	, set_disable_uri	] = useState<boolean>(false);

	const	[ db_options	, set_db_options	] =	useState<DropdownOption[]>([])
	const	[ selected_db	, set_selected_db	] = useState<DropdownOption>(EMPTY_OPTION)	
	const	[ show_db		, set_show_db		] = useState<boolean>(false)
	const	[ disable_db	, set_disable_db	] =	useState<boolean>(true)

	const	[ col_options	, set_col_options	] = useState<DropdownOption[]>([])
	const	[ selected_col	, set_selected_col	] = useState<DropdownOption>(EMPTY_OPTION)	
	const	[ show_col		, set_show_col		] =	useState<boolean>(false)
	const	[ disable_col	, set_disable_col	] =	useState<boolean>(true)

	const	[ col_size		, set_col_size		] =	useState<number>(0)
	const	[ size_input	, set_size_input	] =	useState<number>(0)
	const	[ show_size		, set_show_size		] =	useState<boolean>(false)
	const	[schema_items,  set_schema_items	] =	useState<SchemaItem[]>([])

	const	[ db_data		, set_db_data		] =	useState<any[]>([])
	const	[ show_data		, set_show_data		] =	useState<boolean>(false)
	const	[ disable_data	, set_disable_data	] =	useState<boolean>(true)
	const	[ error_message	, set_error_message	] =	useState<string>('')

	/**
	 * Reset mongo uri
	 */
	const	reset_mongo_uri		=	()	=>	{
		set_mongo_uri('')
		set_disable_uri(true)
	}

	/**
	 * Clears all database selection state.
	 */
	const	reset_database		=	()	=>	{
		set_db_options([])
		set_selected_db(EMPTY_OPTION)
		set_show_db(false)
		set_disable_db(true)
	}

	/**
	 * Clears all collection selection state.
	 */
	const	reset_collection	=	()	=>	{
		set_col_options([])
		set_selected_col(EMPTY_OPTION)
		set_show_col(false)
		set_disable_col(true)
	}

	/**
	 * Clears collection schema and record limit state.
	 */
	const	reset_col_size		=	()	=>	{
		set_col_size(0)
		set_size_input(0)
		set_show_size(false)
		set_schema_items([])
		set_disable_data(true)
	}

	/**
	 * Clears fetched table data.
	 */
	const	reset_data			=	()	=>	{
		set_db_data([])
		set_show_data(false)
		set_disable_data(true)
	}

	/**
	 * Clears state
	 */
	const	reset_state			=	()	=>	{
		set_is_connected(false)
		set_loading(false)
		set_error_message('')
		reset_mongo_uri()
		reset_database()
		reset_collection()
		reset_col_size()
		reset_data()
	}

	/**
	 * Safely closes the active websocket connection.
	 */
	const disconnect_websocket = () => {
		socket_ref.current?.close();
	};

	/**
	 * COnnect to websocket
	 */
	const	connect_to_websocket	=	()	=>	{
		if (token) {
			let path = `ws://${HOST}/ws/mongo?token=${token}`
			socket_ref.current	= new WebSocket(path)

			socket_ref.current.onopen	=	()	=>	{
				console.log("WebSocket connected");
				set_is_connected(true)
			}

			socket_ref.current.onmessage	=	(e: MessageEvent) => {
				try{
					const	res_data	=	e.data
					const	decoded		=	decryptPayload(res_data)

					if (!decoded) {
						set_error_message('No connection')
					}

					if (decoded?.is_error) {
						set_error_message(decoded?.data?.error_message)
						set_disable_uri(true)
					}

					if (decoded?.action === 'INITIALIZE') {
						let data	=	decoded?.data?.database_names
						if (data) {
							set_db_options(data.map((v:string) => ({value:v, label:v})))
							set_show_db(true)
						}
					}

					if (decoded?.action === 'GET_DATABASE') {
						let data	=	decoded?.data?.collection_names
						if (data) {
							set_col_options(data.map((v:string) => ({value:v, label:v})))
							set_show_col(true)
						}
					}

					if (decoded?.action === 'GET_COLLECTION') {
						let data	=	decoded?.data?.data
						if (data) {
							let schema: Record<string, string[]> = data.schema

							set_col_size(data.count)
							set_size_input(data.count)
							set_schema_items(Object.keys(schema).map(k => ({
								label: k,
								type: schema[k][0]
							})))
							set_disable_data(false)
							set_show_size(true)
						}
					}

					if (decoded?.action === 'GET_DATA') {
						let data	:Array<string>=	decoded?.data?.data
						if (data) {
							set_db_data(data)
							set_show_data(true)
							
						}
					}

					if (decoded?.action === 'CLOSE') {
						console.log('close')
					}
					
				} catch (e) {
					set_error_message(`ERROR: ${e}`)
				} finally {
					set_loading(false)

				}
			}
			
			socket_ref.current.onclose		=	()	=>	{
				console.log("WebSocket disconnected");
				reset_state()
			}
			
			socket_ref.current.onerror		=	(e)	=>	{
				console.log("WebSocket error:", e);
				reset_state()
			}

		}

	}

	useEffect(() => {

		reset_state()
		signIn("credentials", { redirect: false })

		return	()	=>	{
			disconnect_websocket()
		}
	}, [])

	/**
	 * Handles Mongo URI input changes.
	 */
	const	on_change_mongo_uri		=	(e:ChangeEvent<HTMLInputElement>)	=>	{
		const	value	=	e.target.value		
		set_mongo_uri(value)
		if (value) {
			set_disable_uri(false)
		} else {
			set_disable_uri(true)
		}
	}

	/**
	 * Handles database selection.
	 */
	const	on_change_database		=	(option:DropdownOption)	=>	{
		if (option !== selected_db) {
			set_disable_db(false)
			set_selected_db(option)
			if (show_col) {
				reset_collection()
			}
			if (show_size) {
				reset_col_size()
			}
			if (show_data) {
				reset_data()
			}
		}
	}

	/**
	 * Handles collection selection.
	 */
	const	on_change_collection	=	(option:DropdownOption)	=>	{
		if (option !== selected_col) {
			set_disable_col(false)
			set_selected_col(option)
			if (show_size) {
				reset_col_size()
			}
			if (show_data) {
				reset_data()
			}
		}
	}

	/**
	 * Handles changes to the requested record count.
	 */
	const	on_change_size_input	=	()	=>	{
		set_disable_data(false)
		if (show_data) {
			reset_data()
		}
	}

	/**
	 * Clears the UI and requests socket closure.
	 */
	const	on_click_clear			=	()	=> {
		set_error_message('')
		reset_state()
		try{
			if (socket_ref.current && socket_ref.current.readyState === WebSocket.OPEN) {
				set_loading(true)
				const	payload		=	{
					'action'	:	"CLOSE",
				}
				const	encrypted	=	encryptPayload(payload) 
				socket_ref.current.send(encrypted);
			}

		} catch (e) {
			set_error_message(`${e}`)
		} 
	}

	/**
	 * Sends the initialization request with the provided Mongo URI.
	 */
	const	on_click_connect		=	async ()	=>	{
		set_error_message('')
		try{
			if (socket_ref.current && socket_ref.current.readyState === WebSocket.OPEN) {
				set_loading(true)
				const	payload		=	{
					'action'	:	"INITIALIZE",
					'token'		:	session?.user?.token,
					'mongo_uri'	:	mongo_uri
				}
				const	encrypted	=	encryptPayload(payload) 
				socket_ref.current.send(encrypted);
			}

		} catch (e) {
			set_error_message(`${e}`)
		} 
	}

	/**
	 * Requests collections for the selected database.
	 */
	const	on_click_get_db			=	async ()	=>	{
		try{
			if (socket_ref.current && socket_ref.current.readyState === WebSocket.OPEN) {
				set_disable_db(true)
				set_error_message('')
				set_loading(true)
				const	payload		=	{
					'action'	:	"GET_DATABASE",
					'token'		:	session?.user?.token,
					'database'	:	selected_db.value
				}
				const	encrypted	=	encryptPayload(payload) 
				socket_ref.current.send(encrypted);
			}

		} catch (e) {
			set_error_message(`${e}`)
		} finally {
			set_loading(false)
		}
	}

	/**
	 * Requests schema information for the selected collection.
	 */
	const	on_click_get_col		=	async ()	=>	{
		try{
			if (socket_ref.current && socket_ref.current.readyState === WebSocket.OPEN) {
				set_disable_col(true)
				set_error_message('')
				set_loading(true)
				const	payload		=	{
					'action'		:	"GET_COLLECTION",
					'token'			:	session?.user?.token,
					'collection'	:	selected_col.value
				}
				const	encrypted	=	encryptPayload(payload) 
				socket_ref.current.send(encrypted);
			}
		} catch (e) {
			set_error_message(`${e}`)
		} finally {
			set_loading(false)
		}
	}

	/**
	 * Requests record data for the current collection.
	 */
	const	on_click_get_data		=	async ()	=>	{
		try{
			if (socket_ref.current && socket_ref.current.readyState === WebSocket.OPEN) {
				set_disable_data(true)
				set_error_message('')
				set_loading(true)
				const	payload		=	{
					'action'	:	"GET_DATA",
					'token'		:	session?.user?.token,
					'limit'		:	size_input
				}
				const	encrypted	=	encryptPayload(payload) 
				socket_ref.current.send(encrypted);
			}
		} catch (e) {
			set_error_message(`${e}`)
		} finally {
			set_loading(false)	
		}
	}


	function	UriInput() {
		function	ConnectButton()	{
			return	<Button 
				children	=	"Connect"
				onClick		=	{on_click_connect}
				disabled	=	{disable_uri}
			/>
		}
		function	ClearButton()	{
			return	<Button 
				children	=	"Clear"
				onClick		=	{on_click_clear}
			/>
		}
		return	<InputRow 
			label			=	{<span style={{fontSize:FONT_SIZE}}>Enter Mongo URI</span>}
			input_element	=	{<ProtectedInput 
									value		=	{mongo_uri}
									onChange	=	{on_change_mongo_uri}
									fontSize	=	{FONT_SIZE}
									readOnly	=	{show_db}
								/>}
			action_button	=	{show_db ? ClearButton() : ConnectButton()}
			show			=	{true}
		/>
	}

	function	DatabaseSelector() {
		return	<InputRow 
			label			=	{<span style={{fontSize:FONT_SIZE}}>Select Database</span>}
			input_element	=	{<Dropdown 
									value		=	{selected_db}
									onChange	=	{on_change_database}
									options		=	{db_options}
									fontSize	=	{FONT_SIZE}
								/>}
			action_button	=	{<Button 
									children="Get"
									onClick={on_click_get_db}
									disabled={disable_db}
								/>}

			show			=	{show_db}
		/>
	}

	function	CollectionSelector() {
		return	<InputRow 
			label			=	{<span style={{fontSize:FONT_SIZE}}>Select Collection</span>}
			input_element	=	{<Dropdown 
									value		={selected_col}
									onChange	={on_change_collection}
									options		={col_options}
									fontSize	={FONT_SIZE}
								/>}
			action_button	=	{<Button 
									children	="Get"
									onClick		={on_click_get_col}
									disabled	=	{disable_col}
								/>}
			show			=	{show_col}
		/>
	}

	function	DataSelector() {

		return	<InputRow 
			label			=	{<span style={{fontSize:FONT_SIZE}}>
									{`Number of records: ${col_size}`}
								</span>}
			input_element	=	{<NumberInput 
									value		=	{size_input}
									set_value	=	{set_size_input}
									fontSize	=	{FONT_SIZE}
									readOnly	=	{false}
									min			=	{0}
									max			=	{col_size}
									on_change	=	{on_change_size_input}
								/>}
			action_button	=	{<Button 
									children	=	"Get"
									onClick		=	{on_click_get_data}
									disabled	=	{disable_data}
								/>}
			show			=	{show_size}
		/>
	}

	function 	DataTable() {
		return	<Card 
			children={<MongoTable 
				schema_items={schema_items}
				data={db_data}
			/>}
		/>		
	}


	return <div className="w-full h-[100dvh] flex flex-col items-center bg-[#202020]"
		style={{
			overflow:'hidden'
		}}
	>
		<div className="w-[80%] h-[100%] mt-[50px] flex flex-col items-center gap-5">
			{is_connected
				?	<div className="w-full  h-[fit-content] ">
						{UriInput()}
						<div className="w-full flex flex-row gap-2 my-5">
							{DatabaseSelector()}
							{CollectionSelector()}
							{DataSelector()}
						</div>
					
						{show_data && DataTable()}
						{error_message && <ErrorCallout message={error_message}/>}
						{/* {loading && <LoaderCard />} */}
						<EllipsesLoader show={loading}/>
					</div>
				:	<Card 	children={<div className="p-[10px]">

						<div className="mb-[10px]">CONNECT TO MONGOBD</div>

						<div className="mb-[10px]">
							<Button 
								children='Connect'
								onClick={() => {
									// set_loading(p => !p)
									connect_to_websocket()
								}}
							/>
						</div>


					</div>}
					/>
			}
		</div>
			
	</div>

}
